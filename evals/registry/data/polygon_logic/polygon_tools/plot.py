import math
from entity import EntityData
import matplotlib.pyplot as plt


def plot_polygon(entity_data: EntityData, sample_num: int = 0, starting_x: float = 0,
                 starting_y: float = 0, starting_direction: float = 90) -> bool:
    x, y = [starting_x], [starting_y]
    direction = starting_direction
    actions = entity_data.get('actions')

    def draw_shape() -> None:
        nonlocal direction
        for i, action in enumerate(actions):
            action, value = action
            if action == "T":
                direction += value
            elif action == "M":
                x_new = x[-1] + value * math.cos(math.radians(direction))
                y_new = y[-1] + value * math.sin(math.radians(direction))
                x.append(x_new)
                y.append(y_new)
                plt.annotate(f"{i}", (x[-1], y[-1]))

    plt.figure()

    draw_shape()

    plt.annotate(f"({x[-1]:.2f}, {y[-1]:.2f})", (x[-1], y[-1]), color="red", xytext=(-20, -20),
                 textcoords='offset points')

    plt.title(f"Sample:{sample_num + 1} - {entity_data.get('shape')}")
    plt.plot(x, y, marker="o")
    plt.grid(True)

    plt.show()
