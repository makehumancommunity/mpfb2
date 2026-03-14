# position types:
#   vertex = vertex coordinate (after posing)
#   mean = mean between two vertex coordinates (after posing)
#   head = pose bone head
#   tail = pose bone tail

_HIGH_CONFIDENCE = "HIGH"
_MEDIUM_CONFIDENCE = "MEDIUM"
_LOW_CONFIDENCE = "LOW"

COCO = []

# 0
COCO.append({
    "type": "vertex",
    "name": "Nose",
    "data": 5134,
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
    "type": "tail",
    "name": "Right Shoulder",
    "data": "upperarm01.R",
    "confidence": _HIGH_CONFIDENCE
    })

# 3
COCO.append({
    "type": "tail",
    "name": "Right Elbow",
    "data": "lowerarm01.R",
    "confidence": _HIGH_CONFIDENCE
    })

# 4
COCO.append({
    "type": "tail",
    "name": "Right Wrist",
    "data": "wrist.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 5
COCO.append({
    "type": "tail",
    "name": "Left Shoulder",
    "data": "upperarm01.L",
    "confidence": _HIGH_CONFIDENCE
    })

# 6
COCO.append({
    "type": "tail",
    "name": "Left Elbow",
    "data": "lowerarm01.L",
    "confidence": _HIGH_CONFIDENCE
    })

# 7
COCO.append({
    "type": "tail",
    "name": "Left Wrist",
    "data": "wrist.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 8
COCO.append({
    "type": "tail",
    "name": "Right Hip",
    "data": "upperleg01.R",
    "confidence": _HIGH_CONFIDENCE
    })

# 9
COCO.append({
    "type": "tail",
    "name": "Right Knee",
    "data": "lowerleg01.R",
    "confidence": _HIGH_CONFIDENCE
    })

# 10
COCO.append({
    "type": "tail",
    "name": "Right Ankle",
    "data": "foot.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 11
COCO.append({
    "type": "tail",
    "name": "Left Hip",
    "data": "upperleg01.L",
    "confidence": _HIGH_CONFIDENCE
    })

# 12
COCO.append({
    "type": "tail",
    "name": "Left Knee",
    "data": "lowerleg01.L",
    "confidence": _HIGH_CONFIDENCE
    })

# 13
COCO.append({
    "type": "tail",
    "name": "Left Ankle",
    "data": "foot.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 14
COCO.append({
    "type": "tail",
    "name": "Right Eye",
    "data": "eye.R",
    "confidence": _LOW_CONFIDENCE
    })

# 15
COCO.append({
    "type": "tail",
    "name": "Left Eye",
    "data": "eye.L",
    "confidence": _LOW_CONFIDENCE
    })

# 16
COCO.append({
    "type": "mean",
    "name": "Right Ear",
    "data": [5434, 5629],
    "confidence": _LOW_CONFIDENCE
    })

# 17
COCO.append({
    "type": "mean",
    "name": "Left Ear",
    "data": [12033, 12226],
    "confidence": _LOW_CONFIDENCE
    })

LEFT_HAND = []

# 0
LEFT_HAND.append({
    "type": "head",
    "name": "Wrist",
    "data": "wrist.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# --- THUMB ---

# 1
LEFT_HAND.append({
    "type": "tail",
    "name": "Thumb 1L",
    "data": "finger1-1.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 2
LEFT_HAND.append({
    "type": "tail",
    "name": "Thumb 2L",
    "data": "finger1-2.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 3
LEFT_HAND.append({
    "type": "tail",
    "name": "Thumb 3L",
    "data": "finger1-3.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 4
LEFT_HAND.append({
    "type": "head",
    "name": "Thumb 4L",
    "data": "finger1-3.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# --- INDEX ---

# 5
LEFT_HAND.append({
    "type": "tail",
    "name": "Index 1L",
    "data": "finger2-1.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 6
LEFT_HAND.append({
    "type": "tail",
    "name": "Index 2L",
    "data": "finger2-2.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 7
LEFT_HAND.append({
    "type": "tail",
    "name": "Index 3L",
    "data": "finger2-3.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 8
LEFT_HAND.append({
    "type": "head",
    "name": "Index 4L",
    "data": "finger2-3.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# --- MIDDLE ---

# 9
LEFT_HAND.append({
    "type": "tail",
    "name": "Middle 1L",
    "data": "finger3-1.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 10
LEFT_HAND.append({
    "type": "tail",
    "name": "Middle 2L",
    "data": "finger3-2.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 11
LEFT_HAND.append({
    "type": "tail",
    "name": "Middle 3L",
    "data": "finger3-3.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 12
LEFT_HAND.append({
    "type": "head",
    "name": "Middle 4L",
    "data": "finger3-3.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# --- RING ---

# 13
LEFT_HAND.append({
    "type": "tail",
    "name": "Ring 1L",
    "data": "finger4-1.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 14
LEFT_HAND.append({
    "type": "tail",
    "name": "Ring 2L",
    "data": "finger4-2.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 15
LEFT_HAND.append({
    "type": "tail",
    "name": "Ring 3L",
    "data": "finger4-3.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 16
LEFT_HAND.append({
    "type": "head",
    "name": "Ring 4L",
    "data": "finger4-3.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# --- Little ---

# 17
LEFT_HAND.append({
    "type": "tail",
    "name": "Little 1L",
    "data": "finger5-1.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 18
LEFT_HAND.append({
    "type": "tail",
    "name": "Little 2L",
    "data": "finger5-2.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 19
LEFT_HAND.append({
    "type": "tail",
    "name": "Little 3L",
    "data": "finger5-3.L",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 20
LEFT_HAND.append({
    "type": "head",
    "name": "Little 4L",
    "data": "finger5-3.L",
    "confidence": _MEDIUM_CONFIDENCE
    })



RIGHT_HAND = []

# 0
RIGHT_HAND.append({
    "type": "head",
    "name": "Wrist",
    "data": "wrist.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# --- THUMB ---

# 1
RIGHT_HAND.append({
    "type": "tail",
    "name": "Thumb 1R",
    "data": "finger1-1.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 2
RIGHT_HAND.append({
    "type": "tail",
    "name": "Thumb 2R",
    "data": "finger1-2.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 3
RIGHT_HAND.append({
    "type": "tail",
    "name": "Thumb 3R",
    "data": "finger1-3.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 4
RIGHT_HAND.append({
    "type": "head",
    "name": "Thumb 4R",
    "data": "finger1-3.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# --- INDEX ---

# 5
RIGHT_HAND.append({
    "type": "tail",
    "name": "Index 1R",
    "data": "finger2-1.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 6
RIGHT_HAND.append({
    "type": "tail",
    "name": "Index 2R",
    "data": "finger2-2.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 7
RIGHT_HAND.append({
    "type": "tail",
    "name": "Index 3R",
    "data": "finger2-3.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 8
RIGHT_HAND.append({
    "type": "head",
    "name": "Index 4R",
    "data": "finger2-3.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# --- MIDDLE ---

# 9
RIGHT_HAND.append({
    "type": "tail",
    "name": "Middle 1R",
    "data": "finger3-1.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 10
RIGHT_HAND.append({
    "type": "tail",
    "name": "Middle 2R",
    "data": "finger3-2.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 11
RIGHT_HAND.append({
    "type": "tail",
    "name": "Middle 3R",
    "data": "finger3-3.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 12
RIGHT_HAND.append({
    "type": "head",
    "name": "Middle 4R",
    "data": "finger3-3.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# --- RING ---

# 13
RIGHT_HAND.append({
    "type": "tail",
    "name": "Ring 1R",
    "data": "finger4-1.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 14
RIGHT_HAND.append({
    "type": "tail",
    "name": "Ring 2R",
    "data": "finger4-2.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 15
RIGHT_HAND.append({
    "type": "tail",
    "name": "Ring 3R",
    "data": "finger4-3.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 16
RIGHT_HAND.append({
    "type": "head",
    "name": "Ring 4R",
    "data": "finger4-3.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# --- Little ---

# 17
RIGHT_HAND.append({
    "type": "tail",
    "name": "Little 1R",
    "data": "finger5-1.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 18
RIGHT_HAND.append({
    "type": "tail",
    "name": "Little 2R",
    "data": "finger5-2.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 19
RIGHT_HAND.append({
    "type": "tail",
    "name": "Little 3R",
    "data": "finger5-3.R",
    "confidence": _MEDIUM_CONFIDENCE
    })

# 20
RIGHT_HAND.append({
    "type": "head",
    "name": "Little 4R",
    "data": "finger5-3.R",
    "confidence": _MEDIUM_CONFIDENCE
    })
