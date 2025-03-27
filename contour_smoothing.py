import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

class ContourSmoothingGUI:
    def __init__(self, image_path):
        # Tkinter 창 초기화
        self.root = tk.Tk()
        self.root.title("Contour Smoothing Control")
        
        # 프레임 생성
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 디스크립터 수를 표시할 라벨 초기화
        self.desc_label = ttk.Label(self.top_frame, text="Descriptors: 32")
        self.desc_label.pack(side=tk.LEFT)
        
        # 이미지 로드 및 초기 윤곽선 추출
        self.img = cv2.imread(image_path)
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(self.gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        self.contour = max(contours, key=cv2.contourArea)
        
        # 복소수 윤곽선 변환
        self.complex_contour = self.contour[:, 0, 0] + 1j * self.contour[:, 0, 1]
        self.fourier_desc = np.fft.fft(self.complex_contour)
        
        # matplotlib 설정
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 마우스 이벤트 연결
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # 초기 플롯
        self.update_plot(32)
        
    def update_plot(self, num_descriptors):
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        
        # 원본 윤곽선 플롯
        self.ax1.plot(self.contour[:, 0, 0], self.contour[:, 0, 1], 'b-')
        self.ax1.set_title('Original Contour')
        self.ax1.axis('equal')
        
        # 스무딩된 윤곽선 계산 및 플롯
        half_desc = num_descriptors // 2
        fourier_desc_filtered = np.zeros_like(self.fourier_desc)
        fourier_desc_filtered[:half_desc] = self.fourier_desc[:half_desc]
        fourier_desc_filtered[-half_desc:] = self.fourier_desc[-half_desc:]
        fourier_desc_filtered[0] = self.fourier_desc[0]
        
        smooth_contour = np.fft.ifft(fourier_desc_filtered)
        x_smooth = smooth_contour.real.astype(int)
        y_smooth = smooth_contour.imag.astype(int)
        
        self.ax2.plot(x_smooth, y_smooth, 'r-')
        self.ax2.set_title('Smoothed Contour')
        self.ax2.axis('equal')
        
        # 캔버스 업데이트
        self.canvas.draw()
        
        # 라벨 업데이트
        self.desc_label.config(text=f"Descriptors: {num_descriptors}")
        
    def on_mouse_move(self, event):
        if event.inaxes:
            # 마우스 x 좌표를 디스크립터 수로 변환 (2~100 범위)
            num_descriptors = int(max(2, min(512, event.xdata)))
            self.update_plot(num_descriptors)
            
    def run(self):
        self.root.mainloop()

# 실행
if __name__ == "__main__":
    image_path = "your_image_path.jpg"  # Replace with your image path
    app = ContourSmoothingGUI(image_path)
    app.run()