from typing import Tuple, AsyncGenerator, Optional
import os
from dotenv import load_dotenv, find_dotenv
from .models import Conversation, Stage, ChatInput, ChatResponse
import logging
import json
from langfuse.decorators import observe, langfuse_context
from .prompts import SYSTEM_PROMPT_TEMPLATES_DE, SYSTEM_PROMPT_TEMPLATES_EN

# Load environment variables (searches upward from CWD to find project .env)
load_dotenv(find_dotenv())

# Language detection removed; language is controlled via override from client

# Import agents AFTER env is loaded so API keys are available during initialization
from .agent import routing_agent, response_agent  # noqa: E402

# Verify at least one API key exists (Scaleway preferred, Groq as fallback)
if not os.getenv('SCALEWAY_API_KEY') and not os.getenv('GROQ_API_KEY'):
    raise ValueError("SCALEWAY_API_KEY or GROQ_API_KEY environment variable must be set")

# Get logger instances
logger = logging.getLogger(__name__)

# Configure Langfuse after load_dotenv()
langfuse_context.configure(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

language = "de"

@observe(as_type="trace", capture_input=False, capture_output=False)
async def process_chat_message(chat_input: ChatInput, conversation: Conversation) -> ChatResponse:
    """Process a chat message and return complete response"""
    try:
        # Update the trace level input/output
        langfuse_context.update_current_trace(
            name=f"Chat Session: {chat_input.session_id[:8]}",
            session_id=chat_input.session_id,
            user_id=chat_input.user_id,
            tags=conversation.stages,
            input=chat_input.message,
            output=None
        )
        
        # Update observation level input/output
        langfuse_context.update_current_observation(
            name="Process Message",
            input=chat_input.message,
            output=None,
            metadata={
                "type": "chat_processing",
                "is_streaming": False,
                "user_id": chat_input.user_id
            }
        )
        
        # Add user message first so stage determination sees it in history
        # Use current conversation language or override for initial tagging
        initial_language = chat_input.language_override or conversation.language
        conversation.add_message(chat_input.message, "user", language=initial_language)

        # Language is controlled by override (from UI) or previous conversation setting
        detected_language = chat_input.language_override or conversation.language or "en"
        stage = await determine_stage_async(chat_input.message, conversation)
        conversation.language = detected_language
        
        response, usage = await get_response_async(stage, chat_input.message, conversation)
        conversation.add_message(response, "assistant", stage, language=detected_language)
        
        response_obj = ChatResponse(
            session_id=chat_input.session_id,
            stage=stage,
            response=response,
            stages=conversation.stages,
            usage=usage,
            language=detected_language
        )
        
        # Update both trace and observation output
        langfuse_context.update_current_trace(
            output=response
        )
        langfuse_context.update_current_observation(
            output=response,
            usage=usage
        )
        
        return response_obj
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise

@observe(as_type="trace", capture_input=False, capture_output=False)
async def process_chat_message_stream(chat_input: ChatInput, conversation: Conversation) -> AsyncGenerator[str, None]:
    """Process a chat message and yield streaming response"""
    try:
        # Update trace level with session, user, input
        langfuse_context.update_current_trace(
            name=f"Streaming Chat Session: {chat_input.session_id[:8]}",
            session_id=chat_input.session_id,
            user_id=chat_input.user_id,
            tags=conversation.stages,
            input=chat_input.message
        )
        
        langfuse_context.update_current_observation(
            name="Process Stream Message",
            input=chat_input.message,
            output=None,
            metadata={
                "type": "chat_processing",
                "is_streaming": True
            }
        )
        
        # Add user message first so stage determination sees it in history
        initial_language = chat_input.language_override or conversation.language
        conversation.add_message(chat_input.message, "user", language=initial_language)

        # Language is controlled by override (from UI) or previous conversation setting
        detected_language = chat_input.language_override or conversation.language or "en"
        stage = await determine_stage_async(chat_input.message, conversation)
        conversation.language = detected_language
        
        history = conversation.get_history_as_string()
        intro_message_de = "AI: Ich bin hier, um dir zu helfen, deine Albträume zu bewältigen und sie in positivere Erfahrungen zu verwandeln.\\nNimm dir Zeit, deinen Albtraum so detailliert wie möglich zu beschreiben. Wenn du fertig bist, werde ich hier sein, um dir Anleitung und Unterstützung zu bieten, während wir ihn gemeinsam in eine positivere Erzählung umwandeln."
        intro_message_en = "AI: I'm here to help you work through your nightmares and turn them into more positive experiences.\\nTake your time to describe your nightmare in as much detail as you can. When you're ready, I'll be here to guide and support you as we reshape it together into a more empowering story."

        is_english = (conversation.language == "en")
        templates = SYSTEM_PROMPT_TEMPLATES_EN if is_english else SYSTEM_PROMPT_TEMPLATES_DE
        intro_message = intro_message_en if is_english else intro_message_de

        # Prepend intro message to the history string used for the prompt
        history_for_prompt = intro_message + "\\n" + history if history else intro_message
        
        prompt_template = templates[stage]
        full_prompt = f"\n\nConversation history:\n{history_for_prompt}"
        
        full_response = ""
        final_usage = {}
        async for chunk, chunk_usage in get_response_stream_async(stage, full_prompt, conversation, detected_language):
            if chunk:
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk, 'stages': conversation.stages, 'language': detected_language})}\n\n"
            if chunk_usage:
                final_usage = chunk_usage
        
        conversation.add_message(full_response, "assistant", stage, language=detected_language)
        
        # Update trace output at the end
        langfuse_context.update_current_trace(
            output=full_response
        )
        langfuse_context.update_current_observation(
            output=full_response,
            usage=final_usage
        )
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Streaming error: {str(e)}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@observe(name="determine_stage", as_type="generation", capture_input=False, capture_output=False)
async def determine_stage_async(user_input: str, conversation: Conversation) -> str:
    """Async version of determine_stage"""
    langfuse_context.update_current_observation(
        name="Stage Determination",
        input=user_input,
        output=None,  # Will be set later
        metadata={"type": "stage_determination"}
    )
    
    history = conversation.get_history_as_string()
    # Corrected prompt: ROUTING_PROMPT is handled by the agent's system_prompt
    prompt = f"<transcript>\n{history}\n</transcript>\n\nClassification:"
    
    stage_response, usage = await routing_agent.generate(prompt)  # Unpack both content and usage
    stage_str = stage_response.strip()
    logger.info(f"Stage output: {stage_str}")
    
    try:
        stage = Stage(stage_str)
    except ValueError:
        print(f"Invalid stage {stage_str}, defaulting to last stage")
        stage = Stage(conversation.stages[-1])

    # *** START ÄNDERUNG ***
    # Diese 'Guard Rail' stellt sicher, dass die Stufen nicht übersprungen werden.
    if stage == Stage.FINAL:
        previous_stages = set(conversation.stages)
        
        # Guard rail 1: Muss eine Zusammenfassung haben, bevor irgendetwas anderes passiert
        # (Wenn keine Zusammenfassung vorhanden ist, leite zu 'summary' um)
        if Stage.SUMMARY.value not in previous_stages:
            print("Redirecting to summary stage as no summary has been generated yet")
            stage = Stage.SUMMARY
            
        # Guard rail 2: Muss ein Rehearsal gehabt haben, bevor es zum Abschluss kommt
        # (Wenn eine Zusammenfassung vorhanden ist, aber kein Rehearsal, leite zu 'rehearsal' um)
        elif Stage.REHEARSAL.value not in previous_stages:
            print("Redirecting to rehearsal stage as no rehearsal has been generated yet")
            stage = Stage.REHEARSAL
    # *** ENDE ÄNDERUNG ***
    
    conversation.stages.append(stage.value)
    
    langfuse_context.update_current_observation(
        output=stage.value,
        metadata={"stage": stage.value},
        usage=usage  # Add usage data to the observation
    )
    
    return stage.value

@observe(name="get_response", as_type="generation", capture_input=False, capture_output=False)
async def get_response_async(stage: str, user_input: str, conversation: Conversation) -> Tuple[str, dict]:
    """Async version of get_response"""
    langfuse_context.update_current_observation(
        name="Response Generation",
        input=user_input,
        output=None,  # Will be set later
        metadata={
            "type": "response_generation",
            "stage": stage
        }
    )
    
    history = conversation.get_history_as_string()
    intro_message_de = "AI: Ich bin hier, um dir zu helfen, deine Albträume zu bewältigen und sie in positivere Erfahrungen zu verwandeln.\\nNimm dir Zeit, deinen Albtraum so detailliert wie möglich zu beschreiben. Wenn du fertig bist, werde ich hier sein, um dir Anleitung und Unterstützung zu bieten, während wir ihn gemeinsam in eine positivere Erzählung umwandeln."
    intro_message_en = "AI: I'm here to help you work through your nightmares and turn them into more positive experiences.\\nTake your time to describe your nightmare in as much detail as you can. When you're ready, I'll be here to guide and support you as we reshape it together into a more empowering story."

    is_english = (conversation.language == "en")
    templates = SYSTEM_PROMPT_TEMPLATES_EN if is_english else SYSTEM_PROMPT_TEMPLATES_DE
    intro_message = intro_message_en if is_english else intro_message_de

    # Prepend intro message to the history string used for the prompt
    history_for_prompt = intro_message + "\\n" + history if history else intro_message
    
    prompt_template = templates[stage]
    full_prompt = f"\n\nConversation history:\n{history_for_prompt}" # Use the modified history
    
    response_agent.system_prompt = prompt_template
    response, usage = await response_agent.generate(full_prompt)
    
    langfuse_context.update_current_observation(
        output=response,
        usage=usage
    )
    
    return response, usage

@observe(name="get_response_stream", as_type="generation", capture_input=False, capture_output=False)
async def get_response_stream_async(stage: str, full_prompt: str, conversation: Conversation, language: str) -> AsyncGenerator[Tuple[str, Optional[dict]], None]:
    """Async streaming version of get_response"""
    langfuse_context.update_current_observation(
        name="Response Generation",
        input=full_prompt,
        output=None,  # Will be set after streaming completes
        metadata={
            "type": "response_generation",
            "stage": stage,
            "language": language,
            "is_streaming": True
        }
    )
    
    is_english = (language == "en")
    templates = SYSTEM_PROMPT_TEMPLATES_EN if is_english else SYSTEM_PROMPT_TEMPLATES_DE
    prompt_template = templates[stage]
    response_agent.system_prompt = prompt_template
    
    full_response = ""
    final_usage = {}
    async for chunk, chunk_usage in response_agent.generate_stream(full_prompt):
        if chunk:
            full_response += chunk
        if chunk_usage:
            final_usage = chunk_usage
        yield chunk, chunk_usage
    
    # Update observation with final output and usage
    langfuse_context.update_current_observation(
        output=full_response,
        usage=final_usage
    )

