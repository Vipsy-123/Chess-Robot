# AutomatedChessRobot

**AutomatedChessRobot** is a cutting-edge project designed to automate chess gameplay on 6 Dof Articulated Robotic Arm by Mitsubishi by leveraging advanced computer vision, machine learning, and robotics. The project integrates the powerful YOLOv5 object detection model, the world-class Stockfish chess engine, and the precise RT Toolbox, all orchestrated through Python.

### Object Detection Flow
![Chess-robot](https://github.com/user-attachments/assets/943e5c9b-c953-40f2-be41-1516096fe48a)

## Key Components

### 1. Detection with YOLOv5
- **YOLOv5** is employed to accurately detect and recognize the positions of chess pieces on the board in real-time.
- The model's robustness allows it to function under various lighting conditions and board setups, ensuring precise detection every time.

### 2. Chess Engine - Stockfish
- The project utilizes the **Stockfish** chess engine, which is renowned for its strategic depth and ability to calculate optimal moves.
- Stockfish ensures the robot can act as a formidable opponent or a helpful partner, depending on the user's preference.

### 3. RT Toolbox
- The **RT Toolbox** is used to control the robotic arm, enabling precise and accurate movement of chess pieces on the board.
- It ensures that each piece is placed correctly according to the rules of chess and the decisions made by the Stockfish engine.

### 4. Python Integration
- **Python** serves as the central language that ties together the vision system, the chess engine, and the robotic arm.
- Python’s flexibility and power allow for seamless communication between components and provide a robust framework for further development.

## Project Workflow
1. **YOLOv5** detects the chess pieces and their positions on the board.
2. The detected positions are passed to the **Stockfish** engine, which calculates the best move based on the current game state.
3. The **RT Toolbox** executes the move by controlling the robotic arm to position the chess pieces accurately.

## Conclusion
The **AutomatedChessRobot** showcases the integration of AI and robotics to create a fully autonomous chess-playing system. By combining advanced detection algorithms, a powerful chess engine, and precise robotic control, this project offers an exciting glimpse into the future of automated systems in gaming.

---

This project is an ongoing development, and contributions are welcome. Feel free to explore, contribute, or reach out with any suggestions or questions.
