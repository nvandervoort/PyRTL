import unittest
import pyrtl
import rtllib
from rtllib import multipliers
import random
import tstcase_utils as utils


class TestWallace(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this is to ensure reproducibility
        random.seed(777906376)

    def setUp(self):
        pyrtl.reset_working_block()

    def tearDown(self):
        pyrtl.reset_working_block()

    def test_wallace_tree_1(self):
        """
        Arithmatic tester version 2015.05
        """

        # Creating the logic nets
        a, b = pyrtl.Input(13, "a"), pyrtl.Input(14, "b")
        product = pyrtl.Output(27, "product")
        product <<= multipliers.tree_multiplier(a, b)

        # creating the testing values and the correct results
        xvals = [int(random.uniform(0, 2**13-1)) for i in range(20)]
        yvals = [int(random.uniform(0, 2**14-1)) for i in range(20)]
        true_result = [i * j for i, j in zip(xvals, yvals)]

        # Setting up and running the tests
        sim_trace = pyrtl.SimulationTrace()
        sim = pyrtl.Simulation(tracer=sim_trace)
        for cycle in range(len(xvals)):
            sim.step({a: xvals[cycle], b: yvals[cycle]})

        # Extracting the values and verifying correctness
        multiplier_result = sim_trace.trace[product]
        self.assertEquals(multiplier_result, true_result)

        # now executing the same test using FastSim
        sim_trace = pyrtl.SimulationTrace()
        sim = pyrtl.FastSimulation(tracer=sim_trace)
        for cycle in range(len(xvals)):
            sim.step({a: xvals[cycle], b: yvals[cycle]})

        multiplier_result = sim_trace.trace[product]
        self.assertEquals(multiplier_result, true_result)
        # test passed!

    def test_wallace_tree_2(self):
        pass

    def test_fma_1(self):
        wires, vals = map(None, *(utils.generate_in_wire_and_values(10) for i in range(3)))
        outwire = pyrtl.Output(21, "test")
        test_w = multipliers.fused_multiply_adder(wires[0], wires[1], wires[2], False)
        self.assertEquals(len(test_w), 20)
        outwire <<= test_w

        sim_trace = pyrtl.SimulationTrace()
        sim = pyrtl.Simulation(tracer=sim_trace)
        for cycle in range(len(vals[0])):
            sim.step({wire: val[cycle] for wire, val in map(None, wires, vals)})

        out_vals = sim_trace.trace[outwire]
        true_result = [vals[0][cycle] * vals[1][cycle] + vals[2][cycle]
                       for cycle in range(len(vals[0]))]
        self.assertEquals(out_vals, true_result)

    def test_gen_fma_1(self):
        # sorry for the low readability
        wires, vals = map(None, *(utils.generate_in_wire_and_values(random.randrange(1,8))
                                  for i in range(8)))
        outwire = pyrtl.Output(name="test")
        # mixing tuples and lists solely for readability purposes
        mult_pairs = [(wires[0], wires[1]), (wires[2], wires[3]), (wires[4], wires[5])]
        add_wires = (wires[6], wires[7])
        outwire <<= multipliers.generalized_fma(mult_pairs, add_wires, signed=False)

        sim_trace = pyrtl.SimulationTrace()
        sim = pyrtl.Simulation(tracer=sim_trace)
        for cycle in range(len(vals[0])):
            sim.step({wire: val[cycle] for wire, val in map(None, wires, vals)})

        out_vals = sim_trace.trace[outwire]
        true_result = [vals[0][cycle] * vals[1][cycle] + vals[2][cycle] * vals[3][cycle] +
                       vals[4][cycle] * vals[5][cycle] + vals[6][cycle] + vals[7][cycle]
                       for cycle in range(len(vals[0]))]
        self.assertEquals(out_vals, true_result)
