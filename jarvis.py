import cv2
import mediapipe as mp
import numpy as np
import time
import ctypes
import pyautogui

# === ⚙️ 参数微调 ===
SMOOTHING = 3           
FRAME_REDUCTION = 80    
CLICK_DIST = 0.05       
SCROLL_SPEED = 20       # 稍微调慢一点点，防止太快晕车

# === 📏 滚动区域阈值 (核心修改) ===
# 0.0 是顶端，1.0 是底端
SCROLL_UP_THRESH = 0.35   # 手高于 35% 区域 -> 上滑
SCROLL_DOWN_THRESH = 0.55 # 手低于 55% 区域 -> 下滑 (原来是0.6，现在更容易触发了)

# === 🛠️ 底层操作 ===
def move_mouse(x, y):
    try: ctypes.windll.user32.SetCursorPos(int(x), int(y))
    except: pass

def click_down():
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0) # Left Down

def click_up():
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0) # Left Up

# === 初始化 ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

user32 = ctypes.windll.user32
w_scr, h_scr = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
cap = cv2.VideoCapture(0)

plocX, plocY = 0, 0
clocX, clocY = 0, 0
pinch_active = False     
close_timer_start = 0    
last_double_click = 0 

print("=== 贾维斯滚轮优化版启动 ===")
print("已开启屏幕辅助线：手在上线以上=上滑，下线以下=下滑")

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1)
    h_cam, w_cam, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # --- 🖌️ 画出辅助线 (让你看清触发区) ---
    # 上滑线 (蓝色)
    cv2.line(img, (0, int(h_cam * SCROLL_UP_THRESH)), (w_cam, int(h_cam * SCROLL_UP_THRESH)), (255, 0, 0), 2)
    cv2.putText(img, "UP ZONE", (10, int(h_cam * SCROLL_UP_THRESH) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    # 下滑线 (蓝色)
    cv2.line(img, (0, int(h_cam * SCROLL_DOWN_THRESH)), (w_cam, int(h_cam * SCROLL_DOWN_THRESH)), (255, 0, 0), 2)
    cv2.putText(img, "DOWN ZONE", (10, int(h_cam * SCROLL_DOWN_THRESH) + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    results = hands.process(img_rgb)
    
    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
            lm = hand_lms.landmark
            
            x1, y1 = lm[8].x, lm[8].y   # 食指
            x2, y2 = lm[12].x, lm[12].y # 中指
            thumb_x, thumb_y = lm[4].x, lm[4].y 
            
            index_up = y1 < lm[6].y
            middle_up = y2 < lm[10].y
            ring_up = lm[16].y < lm[14].y
            pinky_up = lm[20].y < lm[18].y
            
            # === 1. 关闭窗口 ===
            if index_up and middle_up and ring_up and pinky_up:
                if close_timer_start == 0:
                    close_timer_start = time.time()
                hold_time = time.time() - close_timer_start
                cv2.putText(img, f"CLOSING: {3 - int(hold_time)}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                if hold_time > 2.0: 
                    pyautogui.hotkey('alt', 'f4')
                    close_timer_start = 0 
            
            # === 2. 滚动模式 (优化版) ===
            elif index_up and middle_up:
                close_timer_start = 0
                
                # 判断当前手的位置
                if y1 < SCROLL_UP_THRESH: # 在上滑线之上
                    cv2.putText(img, "SCROLL UP", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    pyautogui.scroll(SCROLL_SPEED)
                elif y1 > SCROLL_DOWN_THRESH: # 在下滑线之下 (现在更容易触发了)
                    cv2.putText(img, "SCROLL DOWN", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    pyautogui.scroll(-SCROLL_SPEED)
                else:
                    cv2.putText(img, "STOP", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            # === 3. 移动/点击/双击 ===
            elif index_up:
                close_timer_start = 0
                
                x1_pixel = x1 * w_cam
                y1_pixel = y1 * h_cam
                x3 = np.interp(x1_pixel, (FRAME_REDUCTION, w_cam - FRAME_REDUCTION), (0, w_scr))
                y3 = np.interp(y1_pixel, (FRAME_REDUCTION, h_cam - FRAME_REDUCTION), (0, h_scr))
                x3 = np.clip(x3, 0, w_scr)
                y3 = np.clip(y3, 0, h_scr)
                
                clocX = plocX + (x3 - plocX) / SMOOTHING
                clocY = plocY + (y3 - plocY) / SMOOTHING
                move_mouse(clocX, clocY)
                plocX, plocY = clocX, clocY

                # 双击
                dist_double = np.linalg.norm(np.array([x2, y2]) - np.array([thumb_x, thumb_y]))
                if dist_double < CLICK_DIST:
                    if time.time() - last_double_click > 0.5:
                        pyautogui.doubleClick()
                        last_double_click = time.time()
                        cv2.putText(img, "DOUBLE CLICK", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                # 单击/拖拽
                dist_single = np.linalg.norm(np.array([x1, y1]) - np.array([thumb_x, thumb_y]))
                if dist_single < CLICK_DIST:
                    if not pinch_active:
                        click_down()
                        pinch_active = True
                    cv2.circle(img, (int(x1*w_cam), int(y1*h_cam)), 15, (0, 255, 0), cv2.FILLED)
                else:
                    if pinch_active:
                        click_up()
                        pinch_active = False
            else:
                close_timer_start = 0

    cv2.imshow("Jarvis Scroll Tuned", img)
    if cv2.waitKey(1) & 0xFF == 27: break
    if cv2.getWindowProperty("Jarvis Scroll Tuned", cv2.WND_PROP_VISIBLE) < 1: break

cap.release()
cv2.destroyAllWindows()