# CartPole Controller Using Fuzzy Logic

<p align="center">
  <img src="Images/flc.png" alt="FuzzyLogic" width="600">
</p>

In this project, we developed a **custom fuzzy logic library in Python** and used it to implement a **Fuzzy Logic Controller (FLC)** to balance a pole on a moving cart. Additionally, we created a **real-time visualizer using Pygame** to display the cart-pole states during simulation.  

The cart-pole dynamics are modeled based on the paper [*“Correct equations for the dynamics of the cart-pole system”*](https://coneural.org/florian/papers/05_cart_pole.pdf).  

<p align="center">
  <img src="Images/cartpole_system.png" alt="CartPole System" width="600">
</p>

---

## CartPole Dynamics

**With friction consideration:**  

<p align="center">
  <img src="Images/dynamics_friction.png" alt="Dynamics with Friction" width="600">
</p>

**Without friction consideration:**  

<p align="center">
  <img src="Images/dynamics_frictionless.png" alt="Dynamics without Friction" width="600">
</p>

---

## Membership Function Types

**Zmf**  
<p align="center">
  <img src="Images/zmf.png" alt="Zmf Membership Function" width="600">
</p>

**Smf**  
<p align="center">
  <img src="Images/smf.png" alt="Smf Membership Function" width="600">
</p>

**Gbellmf**  
<p align="center">
  <img src="Images/gbellmf.png" alt="Gbellmf Membership Function" width="600">
</p>

---

## Inputs and Outputs to the Controller

**Inputs:**  
- Pole angle (θ)  
- Pole angular velocity (θ̇)  
- Cart position (x)  
- Cart velocity (ẋ)  

**Output:**  
- Force (f)  

---

## Fuzzification

**Input Membership Functions:**  

<p align="center">
  <img src="Images/member_functions/Inputs_MF.png" alt="Input Membership Functions" width="600">
</p>

---

## Defuzzification

**Output Membership Functions:**  

<p align="center">
  <img src="Images/member_functions/Outputs_MF.png" alt="Output Membership Functions" width="600">
</p>

---
## Result
<p align="center">
  <img src="videos/cartpole_control.gif" alt="Step Response" width="600">
</p>

<p align="center">
  <img src="Images/states.png" alt="Step Response" width="600">
</p>

---
## Usage

```bash
pip install numpy matplotlib pygame
```

```bash
python3 main.py
```

---

## References

- Florian, “Correct equations for the dynamics of the cart-pole system”, [Link](https://coneural.org/florian/papers/05_cart_pole.pdf)  
- Matlab Fuzzy Inference System Modeling , [Link](https://www.mathworks.com/help/fuzzy/fuzzy-inference-system-modeling.html?s_tid=CRUX_topnav)
- Pygame, [Link](https://www.pygame.org/wiki/about)
