import numpy as np
from scipy.spatial import distance

class YOLOTracker:
    def __init__(self, max_disappeared=50):
        self.next_object_id = 0
        self.objects = {}  # object ID -> (centroid, class ID)
        self.disappeared = {}  # object ID -> number of consecutive frames disappeared
        self.max_disappeared = max_disappeared

    def register(self, centroid, class_id):
        self.objects[self.next_object_id] = (centroid, class_id)
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, detections):
        # detections is a list of [x1, y1, x2, y2, confidence, class_id]
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self._format_output()

        input_centroids = []
        input_class_ids = []

        for detection in detections:
            x1, y1, x2, y2, _, class_id = detection
            centroid = ((x1 + x2) // 2, (y1 + y2) // 2)
            input_centroids.append(centroid)
            input_class_ids.append(class_id)

        if len(self.objects) == 0:
            for centroid, class_id in zip(input_centroids, input_class_ids):
                self.register(centroid, class_id)
        else:
            object_ids = list(self.objects.keys())
            object_centroids = [self.objects[obj_id][0] for obj_id in object_ids]

            dist_matrix = distance.cdist(np.array(object_centroids), np.array(input_centroids))
            rows = dist_matrix.min(axis=1).argsort()
            cols = dist_matrix.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for row, col in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                object_id = object_ids[row]
                self.objects[object_id] = (input_centroids[col], input_class_ids[col])
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, dist_matrix.shape[0])) - used_rows
            unused_cols = set(range(0, dist_matrix.shape[1])) - used_cols

            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            for col in unused_cols:
                self.register(input_centroids[col], input_class_ids[col])

        return self._format_output(detections)

    def _format_output(self, detections=None):
        output = []
        for object_id, (centroid, class_id) in self.objects.items():
            x, y = centroid
            for detection in detections or []:
                x1, y1, x2, y2, confidence, class_detected = detection
                if class_detected == class_id and (x, y) == ((x1 + x2) // 2, (y1 + y2) // 2):
                    output.append([x1, y1, x2, y2, confidence, object_id, class_id])
        return output

