# position types:
#   vertex = vertex coordinate (after posing)
#   mean = mean between two vertex coordinates (after posing)
#   head = pose bone head
#   tail = pose bone tail

_STRONG_CONFIDENCE = 0.9
_MEDIUM_CONFIDENCE = 0.5
_LOW_CONFIDENCE = 0.1

COCO = []

# 0
COCO.append({
    "type": "vertex",
    "name": "Nose",
    "data": 201,
    "confidence": _LOW_CONFIDENCE
    })

# 1
COCO.append({
    "type": "mean",
    "name": "Neck",
    "data": [1528, 1596],
    "confidence": _MEDIUM_CONFIDENCE
    })

# 2
COCO.append({
    "type": "head",
    "name": "Right Shoulder",
    "data": "upperarm01.R",
    "confidence": _STRONG_CONFIDENCE
    })

# 3
COCO.append({
    "type": "head",
    "name": "Right Elbow",
    "data": "lowerarm01.R",
    "confidence": _STRONG_CONFIDENCE
    })

# 4
COCO.append({
    "type": "head",
    "name": "Right Wrist",
    "data": "wrist.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 5
COCO.append({
    "type": "head",
    "name": "Left Shoulder",
    "data": "upperarm01.L",
    "confidence": _STRONG_CONFIDENCE
    })

# 6
COCO.append({
    "type": "head",
    "name": "Left Elbow",
    "data": "lowerarm01.L",
    "confidence": _STRONG_CONFIDENCE
    })

# 7
COCO.append({
    "type": "head",
    "name": "Left Wrist",
    "data": "wrist.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 8
COCO.append({
    "type": "tail",
    "name": "Right Hip",
    "data": "upperleg01.R",
    "confidence": _STRONG_CONFIDENCE
    })

# 9
COCO.append({
    "type": "head",
    "name": "Right Knee",
    "data": "lowerleg01.R",
    "confidence": _STRONG_CONFIDENCE
    })

# 10
COCO.append({
    "type": "head",
    "name": "Right Ankle",
    "data": "foot.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 11
COCO.append({
    "type": "tail",
    "name": "Left Hip",
    "data": "upperleg01.L",
    "confidence": _STRONG_CONFIDENCE
    })

# 12
COCO.append({
    "type": "head",
    "name": "Left Knee",
    "data": "lowerleg01.L",
    "confidence": _STRONG_CONFIDENCE
    })

# 13
COCO.append({
    "type": "head",
    "name": "Left Ankle",
    "data": "foot.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 14
COCO.append({
    "type": "head",
    "name": "Right Eye",
    "data": "eye.R",
    "confidence": _LOW_CONFIDENCE
    })

# 15
COCO.append({
    "type": "head",
    "name": "Left Eye",
    "data": "eye.L",
    "confidence": _LOW_CONFIDENCE
    })

# 16
COCO.append({
    "type": "vertex",
    "name": "Right Ear",
    "data": 5543,
    "confidence": _LOW_CONFIDENCE
    })

# 17
COCO.append({
    "type": "vertex",
    "name": "Left Ear",
    "data": 12142,
    "confidence": _LOW_CONFIDENCE
    })
