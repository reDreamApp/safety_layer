#!/usr/bin/env python3
"""
Test script to verify Phase 1 migration is complete and working.
"""

import sys
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables before importing modules that need them
load_dotenv(find_dotenv())

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from AI import agent, models, logging_config, prompts
        print("✅ All AI modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_models():
    """Test that Pydantic models work correctly."""
    print("\nTesting models...")
    
    try:
        from AI.models import Message, Conversation, ChatInput, ChatResponse, Stage
        
        # Test Message creation
        msg = Message(content="Test message", role="user")
        assert msg.content == "Test message"
        assert msg.role == "user"
        print("✅ Message model works")
        
        # Test Conversation creation
        conv = Conversation(session_id="test-123")
        assert conv.session_id == "test-123"
        assert len(conv.messages) == 0
        print("✅ Conversation model works")
        
        # Test Stage enum
        assert Stage.RECORDING.value == "recording"
        print("✅ Stage enum works")
        
        return True
    except Exception as e:
        print(f"❌ Model test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_structure():
    """Test that Agent class structure is correct."""
    print("\nTesting Agent structure...")
    
    try:
        from AI.agent import Agent, ModelConfig, MODELS, routing_agent, response_agent
        
        # Check that MODELS dict exists and has expected keys
        assert "GROQ_70B" in MODELS
        assert "GROQ_8B" in MODELS
        assert "GPT4" in MODELS
        assert "MISTRAL_LARGE" in MODELS
        print("✅ Model configurations exist")
        
        # Check ModelConfig structure
        groq_config = MODELS["GROQ_8B"]
        assert groq_config.name == "llama-3.1-8b-instant"
        assert groq_config.provider == "groq"
        print("✅ ModelConfig structure correct")
        
        # Check agent instances (may be None if API keys not set)
        if routing_agent is None or response_agent is None:
            print("⚠️  Agent instances not created (API keys not set - this is OK for testing)")
        else:
            print("✅ Agent instances created")
        
        return True
    except Exception as e:
        print(f"❌ Agent structure test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompts():
    """Test that prompts are loaded correctly."""
    print("\nTesting prompts...")
    
    try:
        from AI.prompts import ROUTING_PROMPT, SYSTEM_PROMPT_TEMPLATES_DE, SYSTEM_PROMPT_TEMPLATES_EN
        
        assert ROUTING_PROMPT is not None
        assert len(ROUTING_PROMPT) > 0
        print("✅ ROUTING_PROMPT loaded")
        
        assert "recording" in SYSTEM_PROMPT_TEMPLATES_DE
        assert "rewriting" in SYSTEM_PROMPT_TEMPLATES_DE
        assert "summary" in SYSTEM_PROMPT_TEMPLATES_DE
        print("✅ German templates loaded")
        
        assert "recording" in SYSTEM_PROMPT_TEMPLATES_EN
        assert "rewriting" in SYSTEM_PROMPT_TEMPLATES_EN
        assert "summary" in SYSTEM_PROMPT_TEMPLATES_EN
        print("✅ English templates loaded")
        
        return True
    except Exception as e:
        print(f"❌ Prompts test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test that required dependencies are installed."""
    print("\nTesting dependencies...")
    
    dependencies = [
        ("networkx", "NetworkX"),
        ("pandas", "Pandas"),
        ("pydantic", "Pydantic"),
        ("openai", "OpenAI"),
        ("groq", "Groq"),
        ("fastapi", "FastAPI"),
    ]
    
    all_ok = True
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {display_name} installed")
        except ImportError:
            print(f"❌ {display_name} NOT installed")
            all_ok = False
    
    return all_ok

def test_env_file():
    """Check if .env file exists (optional)."""
    print("\nChecking .env file...")
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        print("✅ .env file exists")
        print("   (Note: API keys should be set for full functionality)")
        return True
    else:
        print("⚠️  .env file not found")
        print("   Create .env file with SCALEWAY_API_KEY and MISTRAL_API_KEY for full functionality")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 1 Setup Verification")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Models", test_models()))
    results.append(("Agent Structure", test_agent_structure()))
    results.append(("Prompts", test_prompts()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Environment File", test_env_file()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results[:-1])  # Exclude env file from pass/fail
    env_ok = results[-1][1]
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All core tests passed!")
        if not env_ok:
            print("\n⚠️  Note: .env file not found. Create it to enable API functionality.")
        print("\nReady to proceed to Phase 2!")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
