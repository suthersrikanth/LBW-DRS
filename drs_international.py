"""
International DRS Style Visualization
Creates professional ball-tracking output similar to Hawk-Eye DRS
"""

import cv2
import numpy as np


class InternationalDRS:
    """Creates international-style DRS visualization"""
    
    def __init__(self):
        # Colors
        self.RED = (0, 0, 255)
        self.GREEN = (0, 200, 0)
        self.YELLOW = (0, 255, 255)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (255, 100, 0)
        self.ORANGE = (0, 165, 255)
        
        # Pitch map dimensions
        self.pitch_width = 200
        self.pitch_height = 400
        
        # Wicket view dimensions
        self.wicket_width = 200
        self.wicket_height = 280
        
    def create_pitch_map(self, pitching_status, impact_status, pitching_point=None, 
                         impact_point=None, trajectory=None, show_projection=False):
        """
        Create bird's eye view pitch map with proper stump line zones
        Shows pitching and impact zones with inline/outside indicators
        """
        img = np.zeros((self.pitch_height, self.pitch_width, 3), dtype=np.uint8)
        
        # Background - grass green
        img[:] = (34, 100, 34)
        
        # Pitch strip
        pitch_left = 40
        pitch_right = 160
        pitch_top = 40
        pitch_bottom = 360
        pitch_center = (pitch_left + pitch_right) // 2
        
        # Draw pitch
        cv2.rectangle(img, (pitch_left, pitch_top), (pitch_right, pitch_bottom),
                     (140, 180, 140), -1)
        
        # Pitch texture
        for y in range(pitch_top, pitch_bottom, 8):
            cv2.line(img, (pitch_left, y), (pitch_right, y), (130, 170, 130), 1)
        
        # Draw stump line zones (vertical lines showing off/leg stump lines)
        off_stump_x = pitch_center - 15
        leg_stump_x = pitch_center + 15
        
        # Off stump line (dashed)
        for y in range(pitch_top, pitch_bottom, 10):
            cv2.line(img, (off_stump_x, y), (off_stump_x, min(y + 5, pitch_bottom)), (200, 200, 200), 1)
        
        # Leg stump line (dashed)
        for y in range(pitch_top, pitch_bottom, 10):
            cv2.line(img, (leg_stump_x, y), (leg_stump_x, min(y + 5, pitch_bottom)), (200, 200, 200), 1)
        
        # Middle stump line
        for y in range(pitch_top, pitch_bottom, 10):
            cv2.line(img, (pitch_center, y), (pitch_center, min(y + 5, pitch_bottom)), (150, 150, 150), 1)
        
        # Crease lines
        cv2.line(img, (pitch_left - 15, pitch_top + 20), (pitch_right + 15, pitch_top + 20), 
                self.WHITE, 2)  # Batting crease
        cv2.line(img, (pitch_left - 15, pitch_bottom - 20), (pitch_right + 15, pitch_bottom - 20), 
                self.WHITE, 2)  # Bowling crease
        
        # Stump zone at batting end - draw actual stumps
        stump_top = pitch_top
        stump_bottom = pitch_top + 18
        
        # Draw stump zone box with color based on hitting
        cv2.rectangle(img, (off_stump_x - 3, stump_top), (leg_stump_x + 3, stump_bottom),
                     (80, 80, 80), -1)
        cv2.rectangle(img, (off_stump_x - 3, stump_top), (leg_stump_x + 3, stump_bottom),
                     self.WHITE, 1)
        
        # Draw individual stumps
        for sx in [off_stump_x, pitch_center, leg_stump_x]:
            cv2.line(img, (sx, stump_top + 2), (sx, stump_bottom - 2), self.WHITE, 3)
        
        # Zone labels at bottom
        cv2.putText(img, "OFF", (off_stump_x - 10, pitch_bottom + 18),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.WHITE, 1)
        cv2.putText(img, "LEG", (leg_stump_x - 10, pitch_bottom + 18),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.WHITE, 1)
        
        # Draw trajectory
        if trajectory and len(trajectory) > 1:
            pts = []
            for t in trajectory:
                px = int(pitch_left + t[0] * (pitch_right - pitch_left))
                py = int(pitch_top + 30 + t[1] * (pitch_bottom - pitch_top - 50))
                pts.append((px, py))
            
            for i in range(len(pts) - 1):
                cv2.line(img, pts[i], pts[i+1], self.YELLOW, 2)
        
        # Draw pitching point with zone highlight
        if pitching_point:
            px = int(pitch_left + pitching_point[0] * (pitch_right - pitch_left))
            py = int(pitch_top + 30 + pitching_point[1] * (pitch_bottom - pitch_top - 50))
            
            # Determine color based on status
            if pitching_status == "In Line":
                color = self.GREEN
            elif pitching_status == "Umpire's Call":
                color = self.ORANGE
            else:
                color = self.RED
            
            cv2.circle(img, (px, py), 10, color, -1)
            cv2.circle(img, (px, py), 12, self.WHITE, 2)
            cv2.putText(img, "PITCH", (px - 20, py + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.WHITE, 1)
        
        # Draw impact point
        if impact_point:
            ix = int(pitch_left + impact_point[0] * (pitch_right - pitch_left))
            iy = int(pitch_top + 30 + impact_point[1] * (pitch_bottom - pitch_top - 50))
            
            # Determine color based on status
            if impact_status == "In Line":
                color = self.GREEN
            elif impact_status == "Umpire's Call":
                color = self.ORANGE
            else:
                color = self.RED
            
            cv2.rectangle(img, (ix - 8, iy - 8), (ix + 8, iy + 8), color, -1)
            cv2.rectangle(img, (ix - 10, iy - 10), (ix + 10, iy + 10), self.WHITE, 2)
            cv2.putText(img, "IMPACT", (ix - 22, iy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.WHITE, 1)
            
            # Draw projection line to stumps
            if show_projection:
                cv2.line(img, (ix, iy), (pitch_center, stump_bottom), (0, 255, 255), 2, cv2.LINE_AA)
        
        # Title
        cv2.putText(img, "PITCH MAP", (self.pitch_width//2 - 40, 18),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.WHITE, 1)
        
        return img
    
    def create_wicket_view(self, wicket_status, ball_position=None, hit_zone="middle"):
        """
        Create front view of wickets showing where ball would pass
        wicket_status: "Hitting", "Missing", or "Umpire's Call"
        """
        img = np.zeros((self.wicket_height, self.wicket_width, 3), dtype=np.uint8)
        img[:] = (40, 40, 40)
        
        # Stump dimensions
        stump_left = 40
        stump_right = 160
        stump_top = 50
        stump_bottom = 230
        stump_width = stump_right - stump_left
        
        # Draw stump zone background based on status
        if wicket_status == "Hitting":
            zone_color = self.RED
        elif wicket_status == "Umpire's Call":
            zone_color = self.ORANGE
        else:
            zone_color = self.GREEN
            
        overlay = img.copy()
        cv2.rectangle(overlay, (stump_left, stump_top), (stump_right, stump_bottom),
                     zone_color, -1)
        cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)
        
        # Draw stumps
        stump_positions = [stump_left + stump_width//6, 
                          stump_left + stump_width//2,
                          stump_left + 5*stump_width//6]
        
        for sx in stump_positions:
            cv2.line(img, (sx, stump_top), (sx, stump_bottom), self.WHITE, 4)
        
        # Draw bails
        cv2.line(img, (stump_left, stump_top), (stump_right, stump_top), self.WHITE, 4)
        
        # Draw stump zone outline
        cv2.rectangle(img, (stump_left, stump_top), (stump_right, stump_bottom),
                     self.WHITE, 2)
        
        # Draw ball position with projected path indicator
        if ball_position:
            bx = int(stump_left + ball_position[0] * stump_width)
            by = int(stump_top + (1 - ball_position[1]) * (stump_bottom - stump_top))
            
            # Ball shadow
            cv2.circle(img, (bx + 3, by + 3), 14, (20, 20, 20), -1)
            # Ball color based on status
            if wicket_status == "Hitting":
                ball_color = self.RED
            elif wicket_status == "Umpire's Call":
                ball_color = self.ORANGE
            else:
                ball_color = self.GREEN
            cv2.circle(img, (bx, by), 14, ball_color, -1)
            cv2.circle(img, (bx, by), 16, self.WHITE, 2)
        
        # Labels
        cv2.putText(img, "OFF", (stump_left, stump_bottom + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.WHITE, 1)
        cv2.putText(img, "LEG", (stump_right - 25, stump_bottom + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.WHITE, 1)
        
        # Title based on status
        if wicket_status == "Hitting":
            title = "HITTING STUMPS"
            color = self.RED
        elif wicket_status == "Umpire's Call":
            title = "UMPIRE'S CALL"
            color = self.ORANGE
        else:
            title = "MISSING STUMPS"
            color = self.GREEN
            
        cv2.putText(img, title, (self.wicket_width//2 - 60, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return img
    
    def create_decision_panel(self, pitching_status, impact_status, wickets_status, decision, show_decision=True):
        """
        Create the decision panel showing:
        - Pitching: In Line / Outside Leg / Outside Off / Umpire's Call
        - Impact: In Line / Outside Leg / Outside Off / Umpire's Call
        - Wickets: Hitting / Missing / Umpire's Call
        - Final Decision: OUT / NOT OUT / UMPIRE'S CALL
        """
        panel_width = 250
        panel_height = 220
        
        img = np.zeros((panel_height, panel_width, 3), dtype=np.uint8)
        img[:] = (30, 30, 30)
        
        # Border
        cv2.rectangle(img, (2, 2), (panel_width - 3, panel_height - 3), (80, 80, 80), 2)
        
        # Title
        cv2.putText(img, "LBW REVIEW", (panel_width//2 - 50, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.WHITE, 2)
        cv2.line(img, (10, 35), (panel_width - 10, 35), (80, 80, 80), 1)
        
        # Decision items
        y_start = 65
        y_spacing = 40
        
        items = [
            ("PITCHING", pitching_status),
            ("IMPACT", impact_status),
            ("WICKETS", wickets_status)
        ]
        
        for i, (label, status) in enumerate(items):
            y = y_start + i * y_spacing
            
            # Label
            cv2.putText(img, f"{label}:", (15, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.WHITE, 1)
            
            # Status with color
            status_upper = status.upper()
            if status_upper in ["IN LINE", "INLINE", "HITTING"]:
                color = self.GREEN
            elif "UMPIRE" in status_upper:
                color = self.ORANGE
            else:
                color = self.RED
            
            cv2.putText(img, status_upper, (110, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
        
        # Final decision
        cv2.line(img, (10, 175), (panel_width - 10, 175), (80, 80, 80), 1)
        
        if show_decision:
            if "UMPIRE" in decision.upper():
                decision_color = self.ORANGE
            elif decision == "OUT":
                decision_color = self.RED
            else:
                decision_color = self.GREEN
            cv2.putText(img, decision, (panel_width//2 - 40, 205),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, decision_color, 3)
        else:
            cv2.putText(img, "REVIEWING...", (panel_width//2 - 55, 205),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.YELLOW, 2)
        
        return img
    
    def create_full_drs_panel(self, pitching_status, impact_status, wickets_status,
                              pitching_point=None, impact_point=None, trajectory=None,
                              ball_position=None, decision="NOT OUT", show_decision=True,
                              show_projection=False):
        """
        Create complete DRS analysis panel combining all views
        """
        # Create individual components
        pitch_map = self.create_pitch_map(pitching_status, impact_status, 
                                          pitching_point, impact_point, trajectory,
                                          show_projection=show_projection)
        
        wicket_view = self.create_wicket_view(wickets_status, ball_position)
        
        decision_panel = self.create_decision_panel(pitching_status, impact_status, 
                                                    wickets_status, decision, show_decision)
        
        # Combine panels
        # Layout: Pitch Map | Wicket View | Decision Panel
        total_width = self.pitch_width + self.wicket_width + 250 + 40
        total_height = max(self.pitch_height, self.wicket_height, 200) + 50
        
        combined = np.zeros((total_height, total_width, 3), dtype=np.uint8)
        combined[:] = (25, 25, 25)
        
        # Title bar
        cv2.rectangle(combined, (0, 0), (total_width, 35), (50, 50, 50), -1)
        cv2.putText(combined, "BALL TRACKING - DECISION REVIEW SYSTEM", 
                   (total_width//2 - 180, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.WHITE, 2)
        
        # Place pitch map
        y_offset = 45
        pm_h, pm_w = pitch_map.shape[:2]
        combined[y_offset:y_offset + pm_h, 10:10 + pm_w] = pitch_map
        
        # Place wicket view
        x_offset = self.pitch_width + 20
        wv_h, wv_w = wicket_view.shape[:2]
        wicket_y = y_offset + (pm_h - wv_h) // 2
        combined[wicket_y:wicket_y + wv_h, x_offset:x_offset + wv_w] = wicket_view
        
        # Place decision panel
        dp_h, dp_w = decision_panel.shape[:2]
        x_offset = self.pitch_width + self.wicket_width + 30
        decision_y = y_offset + (pm_h - dp_h) // 2
        combined[decision_y:decision_y + dp_h, x_offset:x_offset + dp_w] = decision_panel
        
        return combined


def generate_international_drs_output(video_path, output_path, trajectory_data):
    """
    Generate international-style DRS output video
    
    Args:
        video_path: Input video path
        output_path: Output video path
        trajectory_data: Dictionary with trajectory, pitching, impact, wicket info
    """
    drs = InternationalDRS()
    
    # Extract data
    trajectory = trajectory_data['trajectory']
    pitching = trajectory_data.get('pitching_point')
    impact = trajectory_data.get('impact_point')
    wicket = trajectory_data['wicket_rect']
    
    # Calculate stump center and dimensions
    stump_x = (wicket[0] + wicket[2]) // 2
    stump_top = wicket[1]
    stump_bottom = wicket[3]
    stump_left = wicket[0]
    stump_right = wicket[2]
    stump_width = stump_right - stump_left
    stump_height = stump_bottom - stump_top
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate projection to stumps based on PITCHING to IMPACT trajectory
    # The ball bounces at pitching point and travels to impact point
    # We extend this line to see where it would hit the stumps (at stump Y level)
    if pitching and impact:
        pitch_pt = (pitching[1], pitching[2])  # x, y of pitching
        impact_pt = (impact[1], impact[2])     # x, y of impact
        
        # Calculate direction from pitching to impact
        dx = impact_pt[0] - pitch_pt[0]
        dy = impact_pt[1] - pitch_pt[1]
        
        # We need to project to the STUMP HEIGHT (Y level), not X position
        # The stumps are at stump_top to stump_bottom Y range
        # Find where the trajectory line crosses the middle of stumps (Y axis)
        stump_mid_y = (stump_top + stump_bottom) // 2
        
        if dy != 0:
            # Calculate how far we need to go in Y direction to reach stump level
            # From impact point, continue in same direction
            t = (stump_mid_y - impact_pt[1]) / dy
            proj_x = impact_pt[0] + t * dx
            projection = (int(proj_x), stump_mid_y)
        else:
            # Ball moving horizontally, project X to stump area
            projection = (stump_x, impact_pt[1])
        
        print(f"  Pitch: ({pitch_pt[0]}, {pitch_pt[1]})")
        print(f"  Impact: ({impact_pt[0]}, {impact_pt[1]})")
        print(f"  Stump Y range: {stump_top} - {stump_bottom}")
        print(f"  Projection: {projection}")
        
    elif impact and len(trajectory) >= 2:
        pre_impact = [(t[1], t[2]) for t in trajectory if t[0] <= impact[0]]
        if len(pre_impact) >= 2:
            points = np.array(pre_impact[-5:])
            coeffs = np.polyfit(points[:, 0], points[:, 1], 1)
            proj_y = np.polyval(coeffs, stump_x)
            projection = (stump_x, int(proj_y))
        else:
            projection = (stump_x, (stump_top + stump_bottom) // 2)
    else:
        projection = (stump_x, (stump_top + stump_bottom) // 2)
    
    # Determine LBW conditions with Umpire's Call zones
    # Umpire's Call: ball clipping stumps (within margin)
    umpires_call_margin = int(stump_width * 0.15)  # 15% of stump width
    
    # PITCHING analysis
    if pitching:
        pitch_x = pitching[1]
        # Outside leg = pitched beyond leg stump line
        if pitch_x > stump_right + umpires_call_margin:
            pitching_status = "Outside Leg"
        elif pitch_x > stump_right:
            pitching_status = "Umpire's Call"  # Clipping leg stump line
        else:
            pitching_status = "In Line"
    else:
        pitching_status = "In Line"
    
    # IMPACT analysis
    if impact:
        impact_x = impact[1]
        # Outside off = impact beyond off stump line
        if impact_x < stump_left - umpires_call_margin:
            impact_status = "Outside Off"
        elif impact_x < stump_left:
            impact_status = "Umpire's Call"  # Clipping off stump line
        elif impact_x > stump_right + umpires_call_margin:
            impact_status = "Outside Leg"
        elif impact_x > stump_right:
            impact_status = "Umpire's Call"
        else:
            impact_status = "In Line"
    else:
        impact_status = "In Line"
    
    # WICKETS analysis - check if ball hitting stumps
    # The impact point height relative to stump height determines if hitting
    # This is the standard LBW check - is the ball at stump height when it hits the pad?
    
    if impact:
        impact_y = impact[2]
        
        # Check if impact Y is within stump height range
        if impact_y < stump_top - umpires_call_margin:
            wickets_status = "Missing"  # Ball too high
        elif impact_y < stump_top:
            wickets_status = "Umpire's Call"  # Clipping top
        elif impact_y > stump_bottom + umpires_call_margin:
            wickets_status = "Missing"  # Ball too low
        elif impact_y > stump_bottom:
            wickets_status = "Umpire's Call"  # Clipping bottom
        else:
            wickets_status = "Hitting"  # Ball at stump height
        
        print(f"  Impact Y: {impact_y}, Stump Y range: {stump_top}-{stump_bottom}")
    else:
        wickets_status = "Hitting"
    
    # Final decision logic
    if pitching_status == "Outside Leg":
        decision = "NOT OUT"
        reason = "Pitched outside leg"
    elif impact_status in ["Outside Off", "Outside Leg"]:
        decision = "NOT OUT"
        reason = f"Impact {impact_status.lower()}"
    elif wickets_status == "Missing":
        decision = "NOT OUT"
        reason = "Missing stumps"
    elif "Umpire's Call" in [pitching_status, impact_status, wickets_status]:
        decision = "UMPIRE'S CALL"
        reason = "Stays with on-field decision"
    else:
        decision = "OUT"
        reason = "Hitting stumps"
    
    print(f"\nLBW Analysis:")
    print(f"  Pitching: {pitching_status}")
    print(f"  Impact: {impact_status}")
    print(f"  Wickets: {wickets_status}")
    print(f"  Decision: {decision} - {reason}")
    
    # Normalize coordinates for pitch map
    pitch_norm = None
    impact_norm = None
    traj_norm = []
    
    if pitching:
        pitch_norm = ((pitching[1] - stump_left) / stump_width + 0.5,
                     pitching[2] / height)
    if impact:
        impact_norm = ((impact[1] - stump_left) / stump_width + 0.5,
                      impact[2] / height)
    
    for t in trajectory:
        tx = (t[1] - stump_left) / stump_width + 0.5
        ty = t[2] / height
        traj_norm.append((tx, ty))
    
    # Ball position on wicket view (normalized 0-1)
    ball_pos = None
    if wickets_status in ["Hitting", "Umpire's Call"] and impact:
        ball_x = 0.5  # Center of stumps
        impact_y = impact[2]
        ball_y = 1 - (np.clip(impact_y, stump_top, stump_bottom) - stump_top) / stump_height
        ball_pos = (ball_x, np.clip(ball_y, 0.1, 0.9))
    
    # Interpolate trajectory
    traj_dict = {t[0]: (t[1], t[2]) for t in trajectory}
    trajectory.sort(key=lambda x: x[0])
    
    if len(trajectory) >= 2:
        for i in range(len(trajectory) - 1):
            f1, x1, y1 = trajectory[i]
            f2, x2, y2 = trajectory[i + 1]
            for f in range(f1, f2):
                if f not in traj_dict:
                    t = (f - f1) / (f2 - f1)
                    traj_dict[f] = (int(x1 + t * (x2 - x1)), int(y1 + t * (y2 - y1)))
    
    start_frame = trajectory[0][0]
    end_frame = trajectory[-1][0]
    impact_frame = impact[0] if impact else end_frame
    
    # Frames to show decision after impact
    decision_delay_frames = int(fps * 1.5)  # 1.5 seconds after impact
    
    # Setup video writer
    # First create a sample panel to get dimensions
    sample_panel = drs.create_full_drs_panel(
        pitching_status, impact_status, wickets_status,
        pitch_norm, impact_norm, traj_norm,
        ball_pos, decision, show_decision=True, show_projection=True
    )
    panel_height, panel_width = sample_panel.shape[:2]
    
    out_width = width + panel_width + 20
    out_height = max(height, panel_height) + 100
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (out_width, out_height))
    
    # Show decision 1.5 seconds after impact
    decision_delay_frames = int(fps * 1.5)
    
    print(f"\nGenerating video...")
    print(f"  Impact frame: {impact_frame}")
    print(f"  Decision shown after frame: {impact_frame + decision_delay_frames}")
    
    # Process video until impact + decision delay + 2 seconds of showing decision
    end_frame = impact_frame + decision_delay_frames + int(fps * 2)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    trajectory_history = []
    last_frame = None
    
    for frame_num in range(end_frame):
        ret, frame = cap.read()
        if not ret:
            # If video ends, use last frame for remaining frames
            if last_frame is not None:
                frame = last_frame.copy()
            else:
                break
        else:
            last_frame = frame.copy()
        
        # Update trajectory history
        if frame_num in traj_dict:
            trajectory_history.append(traj_dict[frame_num])
        
        # Draw trajectory trail
        if len(trajectory_history) > 1:
            for i in range(1, len(trajectory_history)):
                alpha = i / len(trajectory_history)
                color = (0, int(255 * alpha), 255)
                thickness = max(2, int(4 * alpha))
                cv2.line(frame, trajectory_history[i-1], trajectory_history[i], color, thickness)
        
        # Draw current ball
        if frame_num in traj_dict:
            x, y = traj_dict[frame_num]
            cv2.circle(frame, (x, y), 15, (150, 150, 255), 2)
            cv2.circle(frame, (x, y), 10, (255, 255, 255), -1)
        
        # Draw wickets
        cv2.rectangle(frame, (wicket[0], wicket[1]), (wicket[2], wicket[3]), (0, 255, 255), 2)
        stump_w = (wicket[2] - wicket[0]) // 3
        for i in range(3):
            sx = wicket[0] + stump_w // 2 + i * stump_w
            cv2.line(frame, (sx, wicket[1]), (sx, wicket[3]), (0, 255, 255), 2)
        cv2.line(frame, (wicket[0], wicket[1]), (wicket[2], wicket[1]), (0, 255, 255), 3)
        
        # Draw pitching point (after ball pitches)
        if pitching and frame_num >= pitching[0]:
            color = (0, 200, 0) if pitching_status == "In Line" else (0, 165, 255) if "Umpire" in pitching_status else (0, 0, 255)
            cv2.circle(frame, (pitching[1], pitching[2]), 12, color, 2)
            cv2.circle(frame, (pitching[1], pitching[2]), 5, color, -1)
            cv2.putText(frame, "PITCHING", (pitching[1] - 35, pitching[2] - 18),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw impact point (after impact)
        if impact and frame_num >= impact[0]:
            color = (0, 200, 0) if impact_status == "In Line" else (0, 165, 255) if "Umpire" in impact_status else (0, 100, 255)
            cv2.rectangle(frame, (impact[1] - 10, impact[2] - 10),
                         (impact[1] + 10, impact[2] + 10), color, 2)
            cv2.putText(frame, "IMPACT", (impact[1] - 30, impact[2] - 18),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw projected path from IMPACT to WICKETS (AFTER impact)
        # The projection shows where ball would hit the stumps at the SAME HEIGHT as impact
        show_projection = frame_num >= impact_frame
        if show_projection and impact:
            impact_pt = (impact[1], impact[2])
            
            # The wicket hit point is at stump X, at the SAME Y as impact (ball continues at same height)
            # This is the standard DRS visualization
            wicket_hit_pt = (stump_x, impact_pt[1])
            
            # Determine color based on whether it hits stumps
            if stump_top <= impact_pt[1] <= stump_bottom:
                proj_color = (0, 0, 255)  # Red - Hitting stumps
            else:
                proj_color = (0, 255, 0)  # Green - Missing stumps
            
            # Draw the PROJECTED PATH as dots FROM IMPACT TO WICKETS
            num_dots = 10
            for i in range(num_dots + 1):
                t = i / num_dots
                dot_x = int(impact_pt[0] + t * (wicket_hit_pt[0] - impact_pt[0]))
                dot_y = int(impact_pt[1] + t * (wicket_hit_pt[1] - impact_pt[1]))
                cv2.circle(frame, (dot_x, dot_y), 7, (255, 255, 255), -1)
                cv2.circle(frame, (dot_x, dot_y), 5, proj_color, -1)
        
        # Determine if we should show the decision
        show_decision = frame_num >= (impact_frame + decision_delay_frames)
        
        # Create DRS panel (updates based on current frame)
        current_traj = [(tx, ty) for (tx, ty) in traj_norm[:len(trajectory_history)]] if trajectory_history else None
        
        drs_panel = drs.create_full_drs_panel(
            pitching_status if frame_num >= (pitching[0] if pitching else 0) else "Reviewing",
            impact_status if frame_num >= impact_frame else "Reviewing",
            wickets_status if show_projection else "Reviewing",
            pitch_norm if frame_num >= (pitching[0] if pitching else 0) else None,
            impact_norm if frame_num >= impact_frame else None,
            current_traj,
            ball_pos if show_projection else None,
            decision,
            show_decision=show_decision,
            show_projection=show_projection
        )
        
        # Create output frame
        output = np.zeros((out_height, out_width, 3), dtype=np.uint8)
        output[:] = (20, 20, 20)
        
        # Place video frame
        video_y = (out_height - 100 - height) // 2
        output[video_y:video_y + height, 0:width] = frame
        
        # Place DRS panel
        panel_y = (out_height - 100 - panel_height) // 2
        ph, pw = drs_panel.shape[:2]
        output[panel_y:panel_y + ph, width + 20:width + 20 + pw] = drs_panel
        
        # Decision banner at bottom
        banner_y = out_height - 100
        
        if show_decision:
            if "UMPIRE" in decision:
                banner_color = (0, 130, 200)  # Orange
            elif decision == "OUT":
                banner_color = (0, 0, 180)  # Red
            else:
                banner_color = (0, 150, 0)  # Green
            
            cv2.rectangle(output, (0, banner_y), (out_width, out_height), banner_color, -1)
            cv2.putText(output, f"DECISION: {decision}", (30, banner_y + 45),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
            
            # Status indicators
            status_x = 380
            p_color = (100, 255, 100) if pitching_status == "In Line" else (100, 200, 255) if "Umpire" in pitching_status else (100, 100, 255)
            i_color = (100, 255, 100) if impact_status == "In Line" else (100, 200, 255) if "Umpire" in impact_status else (100, 100, 255)
            w_color = (100, 255, 100) if wickets_status == "Hitting" else (100, 200, 255) if "Umpire" in wickets_status else (100, 100, 255)
            
            cv2.putText(output, f"Pitching: {pitching_status.upper()}", (status_x, banner_y + 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, p_color, 2)
            cv2.putText(output, f"Impact: {impact_status.upper()}", (status_x, banner_y + 58),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, i_color, 2)
            cv2.putText(output, f"Wickets: {wickets_status.upper()}", (status_x, banner_y + 81),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, w_color, 2)
        else:
            # Reviewing banner
            cv2.rectangle(output, (0, banner_y), (out_width, out_height), (80, 80, 80), -1)
            cv2.putText(output, "REVIEWING...", (30, banner_y + 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        
        # Branding
        cv2.putText(output, "HAWK-EYE", (out_width - 150, banner_y + 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(output, "BALL TRACKING", (out_width - 170, banner_y + 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        writer.write(output)
        
        if frame_num % 50 == 0:
            print(f"  Frame {frame_num}/{end_frame}")
    
    cap.release()
    writer.release()
    
    # Save final frame
    final_path = output_path.replace('.mp4', '_final.png')
    cv2.imwrite(final_path, output)
    
    print(f"\nOutput saved: {output_path}")
    print(f"Final frame: {final_path}")
    
    return {
        'decision': decision,
        'reason': reason,
        'pitching_status': pitching_status,
        'impact_status': impact_status,
        'wickets_status': wickets_status
    }


if __name__ == "__main__":
    import json
    import sys
    import os
    
    # Create output folder if not exists
    os.makedirs('output', exist_ok=True)
    
    # Load trajectory data from interactive tracker
    try:
        with open('trajectory_data.json', 'r') as f:
            data = json.load(f)
        
        video_path = data.get('video_path', 'ball_tracking.mp4')
        output_path = sys.argv[1] if len(sys.argv) > 1 else 'output/drs_output.mp4'
        
        results = generate_international_drs_output(video_path, output_path, data)
        
        print("\n" + "="*50)
        print("LBW DRS ANALYSIS COMPLETE")
        print("="*50)
        print(f"Pitching: {results['pitching_status'].upper()}")
        print(f"Impact: {results['impact_status'].upper()}")
        print(f"Wickets: {results['wickets_status'].upper()}")
        print(f"Decision: {results['decision']}")
        
    except FileNotFoundError:
        print("No trajectory_data.json found!")
        print("Please run interactive_tracker.py first to mark the ball positions.")
        print("\nUsage:")
        print("  1. python interactive_tracker.py ball_tracking.mp4")
        print("  2. Mark ball positions, pitching, impact, and wickets")
        print("  3. Press 'S' to save")
        print("  4. python drs_international.py")
