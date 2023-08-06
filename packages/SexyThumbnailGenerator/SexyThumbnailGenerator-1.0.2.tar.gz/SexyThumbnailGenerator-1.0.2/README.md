# Sexy Thumbnail Generator
Creates a thumbnail when given a compatible video file. Thumbnail wil be selected based on many criteria. 

# Usage & Installation

```bash
pip install SexyThumbnailGenerator
```

```python
    x = SexyThumbnailGenerator("./video.mp4")
    x.generateSelection() 
    x.save("./image.png") # Pass in a path + a file name
```
