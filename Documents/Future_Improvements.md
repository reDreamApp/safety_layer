# Future Improvements

A simple list of potential optimizations and enhancements for the SafetyCritic system.

---

## Performance Optimizations

### 1. Parallel Segment Classification
**Current**: Segments are classified sequentially (one at a time)
**Proposed**: Use `asyncio.gather()` to classify all segments in parallel

**Benefits**:
- ~50% faster for multi-segment inputs
- 3 segments: 800ms → 400ms

**Implementation**:
```python
# In critic.py, line ~262
classification_tasks = [
    self.classifier.classify_intent(segment.text) 
    for segment in dream_segments
]
node_ids = await asyncio.gather(*classification_tasks, return_exceptions=True)
```

**Considerations**: 
- Test API rate limits
- Add error handling for failed classifications

---

## Feature Enhancements

_(Add future features here)_

---

## Documentation

_(Add documentation improvements here)_
