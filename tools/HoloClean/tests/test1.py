import sys
sys.path.append("..")
from holoclean.holoclean import HoloClean, Session
from holoclean.errordetection.sql_dcerrordetector import SqlDCErrorDetection
from holoclean.errordetection.sql_nullerrordetector import\
    SqlnullErrorDetection

import time


class Testing:
    def __init__(self):
        self.holo_obj = HoloClean(
            holoclean_path="..",         # path to holoclean package
            verbose=True,
            # to limit possible values for training data
            pruning_threshold1=0.0,
            # to limit possible values for training data to less than k values
            pruning_clean_breakoff=6,
            # to limit possible values for dirty data (applied after
            # Threshold 1)
            pruning_threshold2=0.0,
            # to limit possible values for dirty data to less than k values
            pruning_dk_breakoff=6,
            # learning parameters
            learning_iterations=30,
            learning_rate=0.001,
            batch_size=5,
            # number of inferred values
            k_inferred=2
        )
        self.session = Session(self.holo_obj)

    def test(self):

        t1 = time.time()

        # dataset = "data/hospital.csv"
        dataset = "data/address_10.csv"

        print("using dataset: {}".format(dataset))

        # denial_constraints = "data/hospital_constraints.txt"
        denial_constraints = "data/address_ten_constraints.txt"

        print("using denial_constraints: {}".format(denial_constraints))

        # ground_truth = "data/hospital_clean.csv"
        ground_truth = "data/address_10_ground_truth.csv"
        print("using ground_truth: {}".format(ground_truth))

        # uncheck this if you don't have ground truth
        # ground_truth = 0

        # Ingesting Dataset and Denial Constraints
        self.session.load_data(dataset)
        self.session.load_denial_constraints(denial_constraints)

        # Error Detectors: We have two, dc violations and null values

        t3 = time.time()
        detector_list = []
        Dcdetector = SqlDCErrorDetection(self.session)
        Nulldetector = SqlnullErrorDetection(self.session)
        detector_list.append(Dcdetector)
        detector_list.append(Nulldetector)
        self.session.detect_errors(detector_list)

        t4 = time.time()
        if self.holo_obj.verbose:
            self.holo_obj.logger.info("Error detection time:")
            self.holo_obj.logger.info("Error detection time:" + str(t4-t3))

        repaired=self.session.repair()
        repaired.sort('index')
        repaired.repartition(1).write.format('com.databricks.spark.csv').option("header", 'true').save('repaired.csv')


        if ground_truth:
            self.session.compare_to_truth(ground_truth)

        t2 = time.time()
        if self.holo_obj.verbose:
            self.holo_obj.logger.info("Total time:" + str(t2-t1))
            print "Execution finished"

        exit(0)


if __name__ == "__main__":
    new_hc = Testing()
    new_hc.test()
