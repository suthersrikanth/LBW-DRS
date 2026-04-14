"""
Interactive Ball Tracker for LBW DRS
Allows user to manually click and mark:
1. Ball positions (trajectory)
2. Pitching point
3. Impact point
4. Wicket positions

Controls:
- LEFT CLICK: Add ball position to trajectory
- 'p': Mark current click as PITCHING point
- 'i': Mark current click as IMPACT point
- 'w': Start marking WICKETS (click top-left then bottom-right)
- 'n': Next frame
- 'b': Previous frame
- 'j': Jump to specific frame
- 's': Save trajectory and generate output
- 'c': Clear all markings
- 'u': Undo last point
- 'q': Quit
- SPACE: Play/Pause video
"""

import cv2
import numpy as np
import json
from drs_international import generate_international_drs_output


class InteractiveTracker:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        self.current_frame = 0
        self.frame = None
        
        # Trajectory data
        self.trajectory = []  # List of (frame, x, y)
        self.pitching_point = None  # (frame, x, y)
        self.impact_point = None  # (frame, x, y)
        self.wicket_rect = None  # (x1, y1, x2, y2)
        self.wicket_marking = False
        self.wicket_start = None
        
        # Mode
        self.mode = "trajectory"  # trajectory, pitching, impact, wicket
        
        # Playback
        self.playing = False
        
        # Window
        self.window_name = "Interactive Ball Tracker - LBW DRS"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.mode == "wicket":
                if self.wicket_start is None:
                    self.wicket_start = (x, y)
                    print(f"Wicket top-left: ({x}, {y}) - Now click bottom-right")
                else:
                    self.wicket_rect = (self.wicket_start[0], self.wicket_start[1], x, y)
                    print(f"Wicket set: {self.wicket_rect}")
                    self.wicket_start = None
                    self.mode = "trajectory"
            elif self.mode == "pitching":
                self.pitching_point = (self.current_frame, x, y)
                print(f"Pitching point set at frame {self.current_frame}: ({x}, {y})")
                self.mode = "trajectory"
            elif self.mode == "impact":
                self.impact_point = (self.current_frame, x, y)
                print(f"Impact point set at frame {self.current_frame}: ({x}, {y})")
                self.mode = "trajectory"
            else:
                # Add to trajectory
                self.trajectory.append((self.current_frame, x, y))
                print(f"Ball position at frame {self.current_frame}: ({x}, {y})")
    
    def read_frame(self, frame_num):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self.cap.read()
        if ret:
            self.frame = frame
            self.current_frame = frame_num
        return ret
    
    def draw_overlay(self):
        if self.frame is None:
            return None
        
        display = self.frame.copy()
        
        # Draw trajectory
        traj_points = [(t[1], t[2]) for t in self.trajectory]
        if len(traj_points) > 1:
            for i in range(1, len(traj_points)):
                cv2.line(display, traj_points[i-1], traj_points[i], (0, 255, 255), 2)
        
        # Draw trajectory points
        for t in self.trajectory:
            frame, x, y = t
            color = (0, 255, 0) if frame == self.current_frame else (0, 200, 200)
            cv2.circle(display, (x, y), 6, color, -1)
            cv2.circle(display, (x, y), 8, (255, 255, 255), 1)
        
        # Draw pitching point
        if self.pitching_point:
            px, py = self.pitching_point[1], self.pitching_point[2]
            cv2.circle(display, (px, py), 15, (0, 0, 255), 3)
            cv2.circle(display, (px, py), 5, (0, 0, 255), -1)
            cv2.putText(display, "PITCH", (px - 25, py - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Draw impact point
        if self.impact_point:
            ix, iy = self.impact_point[1], self.impact_point[2]
            cv2.rectangle(display, (ix - 12, iy - 12), (ix + 12, iy + 12), (255, 0, 0), 3)
            cv2.putText(display, "IMPACT", (ix - 30, iy - 18),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Draw wickets
        if self.wicket_rect:
            x1, y1, x2, y2 = self.wicket_rect
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 255), 2)
            # Draw stumps
            stump_width = (x2 - x1) // 3
            for i in range(3):
                sx = x1 + stump_width // 2 + i * stump_width
                cv2.line(display, (sx, y1), (sx, y2), (0, 255, 255), 2)
            cv2.line(display, (x1, y1), (x2, y1), (0, 255, 255), 3)  # Bails
            cv2.putText(display, "STUMPS", (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        # Draw wicket marking in progress
        if self.wicket_start:
            cv2.circle(display, self.wicket_start, 5, (0, 255, 255), -1)
            cv2.putText(display, "Click bottom-right of stumps", (10, self.height - 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Info panel
        panel_height = 160
        cv2.rectangle(display, (0, 0), (350, panel_height), (0, 0, 0), -1)
        cv2.rectangle(display, (0, 0), (350, panel_height), (100, 100, 100), 1)
        
        y_pos = 25
        cv2.putText(display, f"Frame: {self.current_frame}/{self.total_frames}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y_pos += 25
        cv2.putText(display, f"Mode: {self.mode.upper()}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        y_pos += 25
        cv2.putText(display, f"Trajectory points: {len(self.trajectory)}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_pos += 20
        cv2.putText(display, f"Pitching: {'SET' if self.pitching_point else 'Not set'}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255) if self.pitching_point else (150, 150, 150), 1)
        y_pos += 20
        cv2.putText(display, f"Impact: {'SET' if self.impact_point else 'Not set'}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0) if self.impact_point else (150, 150, 150), 1)
        y_pos += 20
        cv2.putText(display, f"Wickets: {'SET' if self.wicket_rect else 'Not set'}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255) if self.wicket_rect else (150, 150, 150), 1)
        
        # Controls help
        help_y = self.height - 40
        cv2.rectangle(display, (0, help_y - 5), (self.width, self.height), (0, 0, 0), -1)
        cv2.putText(display, "CLICK: Add point | P: Pitching | I: Impact | W: Wickets | N/B: Next/Prev | S: Save | Q: Quit",
                   (10, help_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return display
    
    def run(self):
        print("\n" + "="*60)
        print("INTERACTIVE BALL TRACKER - LBW DRS")
        print("="*60)
        print("\nControls:")
        print("  LEFT CLICK  - Add ball position")
        print("  P           - Mark PITCHING point (then click)")
        print("  I           - Mark IMPACT point (then click)")
        print("  W           - Mark WICKETS (click top-left, then bottom-right)")
        print("  N / ->      - Next frame")
        print("  B / <-      - Previous frame")
        print("  J           - Jump to frame")
        print("  U           - Undo last point")
        print("  C           - Clear all")
        print("  S           - Save and generate DRS output")
        print("  SPACE       - Play/Pause")
        print("  Q / ESC     - Quit")
        print("="*60 + "\n")
        
        self.read_frame(0)
        
        while True:
            # Auto-advance if playing
            if self.playing:
                self.current_frame += 1
                if self.current_frame >= self.total_frames:
                    self.current_frame = 0
                self.read_frame(self.current_frame)
            
            display = self.draw_overlay()
            if display is not None:
                cv2.imshow(self.window_name, display)
            
            key = cv2.waitKey(30 if self.playing else 0) & 0xFF
            
            if key == ord('q') or key == 27:  # Q or ESC
                break
            elif key == ord('n') or key == 83:  # N or Right arrow
                self.playing = False
                self.current_frame = min(self.current_frame + 1, self.total_frames - 1)
                self.read_frame(self.current_frame)
            elif key == ord('b') or key == 81:  # B or Left arrow
                self.playing = False
                self.current_frame = max(self.current_frame - 1, 0)
                self.read_frame(self.current_frame)
            elif key == ord(' '):  # Space - play/pause
                self.playing = not self.playing
            elif key == ord('p'):
                self.mode = "pitching"
                print("Mode: PITCHING - Click to mark pitching point")
            elif key == ord('i'):
                self.mode = "impact"
                print("Mode: IMPACT - Click to mark impact point")
            elif key == ord('w'):
                self.mode = "wicket"
                self.wicket_start = None
                print("Mode: WICKET - Click top-left corner of stumps")
            elif key == ord('j'):
                self.playing = False
                frame_input = input("Enter frame number: ")
                try:
                    frame_num = int(frame_input)
                    if 0 <= frame_num < self.total_frames:
                        self.current_frame = frame_num
                        self.read_frame(self.current_frame)
                except:
                    print("Invalid frame number")
            elif key == ord('u'):
                if self.trajectory:
                    removed = self.trajectory.pop()
                    print(f"Removed point: {removed}")
            elif key == ord('c'):
                self.trajectory = []
                self.pitching_point = None
                self.impact_point = None
                self.wicket_rect = None
                print("Cleared all markings")
            elif key == ord('s'):
                self.save_and_generate()
        
        self.cap.release()
        cv2.destroyAllWindows()
    
    def save_and_generate(self):
        """Save trajectory and generate DRS output"""
        if len(self.trajectory) < 3:
            print("Need at least 3 trajectory points!")
            return
        
        if not self.wicket_rect:
            print("Please mark the wickets first (press W)")
            return
        
        print("\nSaving trajectory and generating DRS output...")
        
        # Save trajectory data
        data = {
            'trajectory': self.trajectory,
            'pitching_point': self.pitching_point,
            'impact_point': self.impact_point,
            'wicket_rect': self.wicket_rect,
            'video_path': self.video_path,
            'width': self.width,
            'height': self.height,
            'fps': self.fps
        }
        
        with open('trajectory_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Saved trajectory_data.json")
        
        # Generate International DRS output
        import os
        os.makedirs('output', exist_ok=True)
        print("\nGenerating International DRS style output...")
        generate_international_drs_output(self.video_path, "output/drs_output.mp4", data)


if __name__ == "__main__":
    import sys
    
    video_path = sys.argv[1] if len(sys.argv) > 1 else "ball_tracking.mp4"
    
    tracker = InteractiveTracker(video_path)
    tracker.run()
