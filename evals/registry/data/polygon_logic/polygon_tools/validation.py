from logger_config import logger
import math

from entity import Polygon


class PolygonValidator:
    @staticmethod
    def is_valid_polygon(polygon: Polygon) -> bool:
        x = [vertex.x for vertex in polygon.vertices]
        y = [vertex.y for vertex in polygon.vertices]
        return math.hypot(x[0] - x[-1], y[0] - y[-1]) < 0.01 and len(set(tuple(point) for point in zip(x, y))) >= 3

    @staticmethod
    def is_final_position_correct(polygon: Polygon) -> bool:
        target_position = [float(i) for i in polygon.entity_data.get('current_position')]
        last_vertex = polygon.vertices[-1]
        return abs(last_vertex.x - target_position[0]) < 0.01 and abs(last_vertex.y - target_position[1]) < 0.01

    @staticmethod
    def is_distance_correct(polygon: Polygon) -> bool:
        target_distance = polygon.entity_data.get('distance_to_origin')
        actual_distance = polygon.grid.position.distance_to_origin()
        return abs(actual_distance - target_distance) < 0.01

    def validate(self, polygon: Polygon) -> bool:
        is_valid_polygon = self.is_valid_polygon(polygon)
        logger.info(f"Is valid polygon: {is_valid_polygon}")
        is_final_position_correct = self.is_final_position_correct(polygon)
        logger.info(f"Is final position correct: {is_final_position_correct}")
        is_distance_correct = self.is_distance_correct(polygon)
        logger.info(f"Is distance correct: {is_distance_correct}")

        valid = is_valid_polygon and is_final_position_correct and is_distance_correct
        logger.info(f"Plot is valid: {valid}")
        return valid
