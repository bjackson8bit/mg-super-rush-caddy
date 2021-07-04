import os
from datetime import datetime
class OutputConn:
    def __init__(self) -> None:
        now = datetime.now()
        self.output_file = './mgsr-events/' + now.strftime("%Y-%m-%d_%H_%M_%S") + "_scores" + ".json"

    def write_rows(self, row_data):
        print(f"Writing score data to file {self.output_file}")
        if not os.path.exists("./mgsr-events"):
            os.makedirs("./mgsr-events")
        with open(self.output_file, 'w') as file:
            file.write("Score,Hole")
            file.write('\n')
            for row in row_data:
                file.write(",".join(row))
                file.write('\n')