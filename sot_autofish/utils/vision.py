import cv2

def is_fish_reeled_in(frame):
    template = cv2.imread("rod_up_template.png", 0)
    res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    return np.max(res) > 0.8  # Match threshold
