# File:"D:\02_Study\01_PHD\09_Test_QH\01_Data\disturbance_gen.py", generated on MON, OCT 23 2023   9:56, PSS(R)E release 35.04.02
psspy.increment_gref(101,r"""1""",0.05)
psspy.dist_machine_trip(3011,r"""1""")
psspy.run(0,5.0,0,0,0)
