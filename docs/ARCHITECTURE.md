# SafeStack AI — System Architecture & Engineering Specification

## 1. Executive Overview

SafeStack AI transforms passive warehouse surveillance into proactive damage prevention. The system observes loading and unloading bays in real time, computes sub-second kinematic telemetry, identifies a curated taxonomy of 10 damage-causing behaviors, calculates a multi-factor graded risk score, and presents operational intelligence through a live supervisor dashboard and a zero-fabrication conversational copilot.

```
+---------------------------------------------------------------------------------------------------+
|                                      SAFESTACK AI ARCHITECTURE                                    |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [ CCTV / RTSP / Video Stream ]                                                                   |
|               |                                                                                   |
|               v                                                                                   |
|  +---------------------------+       +----------------------------+                               |
|  |   YOLOv11 Object Detector | ----> |  DeepSORT / ByteTrack      |                               |
|  |   (Person, Carton, Pallet)|       |  Multi-Frame Tracker       |                               |
|  +---------------------------+       +----------------------------+                               |
|                                                     |                                             |
|                                                     v                                             |
|                                      +----------------------------+                               |
|                                      | Kinematics Physics Engine  |                               |
|                                      | (ay, v_drop, Ek, theta)    |                               |
|                                      +----------------------------+                               |
|                                                     |                                             |
|                                                     v                                             |
|                                      +----------------------------+                               |
|                                      | Sequence Action Classifier |                               |
|                                      | (10 Predefined Behaviors)  |                               |
|                                      +----------------------------+                               |
|                                                     |                                             |
|                                                     v                                             |
|                                      +----------------------------+                               |
|                                      | Graded Risk Scoring Model  |                               |
|                                      | (Low, Med, High, Critical) |                               |
|                                      +----------------------------+                               |
|                                                     |                                             |
|                      +------------------------------+------------------------------+              |
|                      |                                                             |              |
|                      v                                                             v              |
|       +-----------------------------+                               +---------------------------+ |
|       | Responsible AI Shield       |                               | SQLite / Postgres DB      | |
|       | (Face Blur & Silhouette)    |                               | & S3 Video Clip Store     | |
|       +-----------------------------+                               +---------------------------+ |
|                      |                                                             |              |
|                      v                                                             v              |
|       +-----------------------------+                               +---------------------------+ |
|       | React 18 + Chart.js         | <====== WebSocket / REST ===> | Grounded Assistant (RAG)  | |
|       | Supervisor Dashboard        |                               | & 5-Why RCA Generator     | |
|       +-----------------------------+                               +---------------------------+ |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Core Processing Pipeline

1. **Object Detection**:
   - Classifies workers, packages/cartons, pallets, forklifts, and pedestrian walkways.
   - Operates at up to 30 FPS at 1080p resolution.

2. **Multi-Frame Tracking & Trajectories**:
   - Associates bounding boxes across sequential temporal frames using Intersection-over-Union (IoU) and velocity smoothing.
   - Extracts instantaneous velocity vectors $(\vec{v} = (\frac{\Delta x}{\Delta t}, \frac{\Delta y}{\Delta t}))$ and vertical accelerations $(a_y = \frac{\Delta v_y}{\Delta t})$.

3. **Kinematic Physics Engine**:
   - Freefall acceleration verification: $a_y \approx 9.8\text{ m/s}^2$.
   - Kinetic impact energy calculation: $E_k = \frac{1}{2} m v^2$.
   - Landing deceleration impulse: $a_{\text{impact}} = \frac{v_{\text{drop}}}{\Delta t_{\text{impact}}}$.
   - Tilt angle calculation: $\theta = \arctan(\frac{|\Delta x|}{\Delta y})$.
   - Pallet overhang ratio: $\frac{\text{Overhang Length}}{\text{Carton Width}} \times 100\%$.

4. **Sequence-Level Action Recognition**:
   - Analyzes temporal sliding windows (30–60 frames) rather than isolated single frames to prevent false alarms from momentary occlusions or safe hand adjustments.

5. **Graded Risk Scoring Model**:
   $$\text{Score} = \text{clamp}\left(\Big(B \cdot w_b + I \cdot w_i\Big) \cdot C^{0.65} \cdot F, \ 0, \ 100\right)$$
   - Tiers: Low ($<40$), Medium ($40-69$), High ($70-84$), Critical ($85-100$).
