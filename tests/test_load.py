"""

"""

from fixtures import *

sys.path.insert(0, os.path.abspath("../"))

# Adopted units: N and m
kilo = 1e3
milli = 1e-3
N = 1
m = 1
mm = milli * m
m2 = m**2
m3 = m**3
m4 = m**4
kN = kilo * N
MPa = N / ((mm) ** 2)
GPa = kilo * MPa


# =====================================================================================================================
# Tests
# =====================================================================================================================
def test_inputs():
    with pytest.raises(ValueError) as e_info:
        vertex_errors = og.create_load_vertex(x=3, y=0, z=3)
        vertex_errors = og.create_load_vertex()


# test to check compound load position relative to global are correct
def test_compound_load_positions():
    #
    location = og.create_load_vertex(x=5, z=-2, p=20)  # create load point
    Single = og.create_load(loadtype="point", name="single point", point1=location)
    # front_wheel = PointLoad(name="front wheel", localpoint1=LoadPoint(2, 0, 2, 50))
    # Line load
    barrierpoint_1 = og.create_load_vertex(x=-1, z=0, p=2)
    barrierpoint_2 = og.create_load_vertex(x=11, z=0, p=2)
    Barrier = og.LineLoading(point1=barrierpoint_1, point2=barrierpoint_2)

    M1600 = og.create_compound_load(name="Lane and Barrier")
    M1600.add_load(load_obj=Single)
    M1600.add_load(
        load_obj=Barrier
    )  # this overwrites the current global pos of line load
    # the expected midpoint (reference point initial is 6,0,0) is now at 9,0,5 (6+3, 0+0, 5+0)
    # when setting the global coordinate, the global coordinate is added with respect to ref point (9,0,5)
    # therefore (3+4, 0+0, 3+5) = (13,0,8)
    # M1600.set_global_coord(og.Point(4, 0, 3))
    a = 2
    # check if point Single is same as point Single's load vertex
    assert M1600.compound_load_obj_list[0].load_point_1 == og.LoadPoint(
        x=5, y=0, z=-2, p=20
    )
    assert M1600.compound_load_obj_list[1].load_point_1 == og.LoadPoint(
        x=-1, y=0, z=0, p=2
    )
    assert M1600.compound_load_obj_list[1].load_point_2 == og.LoadPoint(
        x=11.0, y=0, z=0, p=2
    )

    # now we set global and see if correct
    M1600.set_global_coord(og.Point(4, 0, 3))
    assert M1600.compound_load_obj_list[0].load_point_1 == og.LoadPoint(
        x=9, y=0, z=1, p=20
    )
    assert M1600.compound_load_obj_list[1].load_point_1 == og.LoadPoint(
        x=3, y=0, z=3, p=2
    )
    assert M1600.compound_load_obj_list[1].load_point_2 == og.LoadPoint(
        x=15.0, y=0, z=3, p=2
    )


def test_point_load_getter(
    bridge_model_42_negative,
):  # test get_point_load_nodes() function
    # test if setter and getter is correct              # and assign_point_to_node() function

    example_bridge = bridge_model_42_negative
    # create reference point load
    location = og.create_load_vertex(x=5, y=0, z=2, p=20)
    Single = og.create_load(
        loadtype="point", name="single point", point1=location, shape_function="hermite"
    )
    ULS_DL = og.create_load_case(name="Point")
    ULS_DL.add_load(Single)  # ch
    example_bridge.add_load_case(ULS_DL)
    og.ops.wipe()
    #
    # assert example_bridge.load_case_list[0]["load_command"] == [
    #     "ops.load(12, *[0, 0.6075807082987842, 0, 0.37389582049155967, 0, 0.34166943132701877])\n",
    #     "ops.load(17, *[0, 1.4724192917012129, 0, 0.9061041795084391, 0, -0.613915767971676])\n",
    #     "ops.load(18, *[0, 12.685458513118162, 0, -3.6244167180337583, 0, -5.289120462525217])\n",
    #     "ops.load(13, *[0, 5.234541486881841, 0, -1.4955832819662394, 0, 2.943613562202012])\n",
    # ]
    # reference_command = example_bridge.load_case_list[0]["load_command"]
    #
    # assert reference_command
    import re

    def parse_load_cmd(cmd):
        # Extract node ID and list of floats from string like: ops.load(12, *[0, np.float64(x), 0, ...])
        match = re.match(r"ops\.load\((\d+), \*\[([^\]]+)\]\)", cmd.strip())
        assert match, f"Failed to parse: {cmd}"
        node = int(match.group(1))
        values = [
            float(x.split("(")[-1].rstrip(")"))
            for x in match.group(2).split(",")
            if "np.float64" in x
        ]
        return node, values

    expected_cmds = [
        (12, [0.6075807082987873, 0.3738958204915613, 0.34166943132702027]),
        (17, [1.4724192917012136, 0.9061041795084389, -0.6139157679716769]),
        (18, [12.685458513118142, -3.624416718033756, -5.289120462525214]),
        (13, [5.234541486881858, -1.4955832819662453, 2.94361356220202]),
    ]

    for cmd_str, (exp_node, exp_vals) in zip(
        example_bridge.load_case_list[0]["load_command"], expected_cmds
    ):
        node, values = parse_load_cmd(cmd_str)
        assert node == exp_node
        for a, b in zip(values, exp_vals):
            assert abs(a - b) < 1e-9  # tolerance for float comparison

    # assert example_bridge.load_case_list[0]["load_command"] == [
    #     "ops.load(12, *[0, np.float64(0.6075807082987873), 0, np.float64(0.3738958204915613), 0, np.float64(0.34166943132702027)])\n",
    #     "ops.load(17, *[0, np.float64(1.4724192917012136), 0, np.float64(0.9061041795084389), 0, np.float64(-0.6139157679716769)])\n",
    #     "ops.load(18, *[0, np.float64(12.685458513118142), 0, np.float64(-3.624416718033756), 0, np.float64(-5.289120462525214)])\n",
    #     "ops.load(13, *[0, np.float64(5.234541486881858), 0, np.float64(-1.4955832819662453), 0, np.float64(2.94361356220202)])\n",
    # ]


# test point load returning None when point (loadpoint) is outside of mesh
def test_point_load_outside_straight_mesh(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    location = og.create_load_vertex(x=5, y=0, z=-2, p=20)
    Single = og.create_load(loadtype="point", name="single point", point1=location)
    ULS_DL = og.create_load_case(name="Point")
    ULS_DL.add_load(Single)  # ch
    example_bridge.add_load_case(ULS_DL)
    grid_nodes, _ = example_bridge._get_point_load_nodes(point=location)
    assert grid_nodes is None


# test general line with line load in the bounds of the mesh
def test_line_load(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=3, y=0, z=3, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=3, p=2)
    Barrier = og.create_load(
        name="Barrier curb load",
        point1=barrierpoint_1,
        point2=barrierpoint_2,
    )
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze()
    example_bridge.get_results()
    ref_answer = [
        {
            7: {
                "long_intersect": [],
                "trans_intersect": [[3.1514141550424406, 0, 3.0]],
                "edge_intersect": [],
                "ends": [[3, 0, 3]],
            },
            8: {
                "long_intersect": [],
                "trans_intersect": [
                    [3.1514141550424406, 0, 3.0],
                    [4.276919210414739, 0, 3.0],
                ],
                "edge_intersect": [],
                "ends": [],
            },
            11: {
                "long_intersect": [],
                "trans_intersect": [
                    [4.276919210414739, 0, 3.0],
                    [5.4024242657870385, 0, 3.0],
                ],
                "edge_intersect": [],
                "ends": [],
            },
            16: {
                "long_intersect": [],
                "trans_intersect": [
                    [5.4024242657870385, 0, 3.0],
                    [6.302828310084881, 0, 3.0],
                ],
                "edge_intersect": [],
                "ends": [],
            },
            22: {
                "long_intersect": [],
                "trans_intersect": [
                    [6.302828310084881, 0, 3.0],
                    [7.227121232563658, 0, 3.0],
                ],
                "edge_intersect": [],
                "ends": [],
            },
            31: {
                "long_intersect": [],
                "trans_intersect": [[10.0, 0, 3.0]],
                "edge_intersect": [],
                "ends": [[10, 0, 3]],
            },
            32: {
                "long_intersect": [],
                "trans_intersect": [[10.0, 0, 3.0], [9.075707077521221, 0, 3.0]],
                "edge_intersect": [],
                "ends": [[10, 0, 3]],
            },
            56: {
                "long_intersect": [],
                "trans_intersect": [
                    [7.227121232563658, 0, 3.0],
                    [8.15141415504244, 0, 3.0],
                ],
                "edge_intersect": [],
                "ends": [],
            },
            62: {
                "long_intersect": [],
                "trans_intersect": [
                    [8.15141415504244, 0, 3.0],
                    [9.075707077521221, 0, 3.0],
                ],
                "edge_intersect": [],
                "ends": [],
            },
        }
    ]
    for grid_key, intersect_dict in example_bridge.global_line_int_dict[0].items():
        assert grid_key in ref_answer[0].keys()  # check keys is correct

        for intersect_type, grid_val in intersect_dict.items():
            # check values
            if grid_val:
                assert grid_val[0] == pytest.approx(
                    ref_answer[0][grid_key][intersect_type][0]
                )


# test line load function with line load is vertical (slope = infinite) and start end points
def test_line_load_vertical_and_cross_outside_mesh(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=2, y=0, z=-3, p=2)
    barrierpoint_2 = og.create_load_vertex(x=2, y=0, z=8, p=2)
    Barrier = og.create_load(
        loadtype="line",
        name="Barrier curb load",
        point1=barrierpoint_1,
        point2=barrierpoint_2,
        shape_function="hermite",
    )
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)
    ref_ans = {
        1: {
            "long_intersect": [[2, 0, 0.0], [2, 0, 1.0]],
            "trans_intersect": [],
            "edge_intersect": [],
            "ends": [],
        },
        3: {
            "long_intersect": [[2, 0, 1.0]],
            "trans_intersect": [],
            "edge_intersect": [[2.0, 0, 2.2212250296583864]],
            "ends": [],
        },
    }
    for grid_key, intersect_dict in example_bridge.global_line_int_dict[0].items():
        assert grid_key in ref_ans.keys()  # check keys is correct

        for intersect_type, grid_val in intersect_dict.items():
            # check values
            if grid_val:
                assert grid_val[0] == pytest.approx(
                    ref_ans[grid_key][intersect_type][0]
                )


# test a line load which coincide with edge z = 0 or z = 7
def test_line_load_coincide_long_edge(bridge_model_42_negative):
    # when set line load z coordinate to z = 0 , test if line returns correct coincide node lines
    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=4, y=0, z=1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=1, p=2)
    Barrier = og.create_load(
        loadtype="line",
        name="Barrier curb load",
        point1=barrierpoint_1,
        point2=barrierpoint_2,
    )
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    ref_answer = [
        {
            5: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[4, 0, 1]],
            },
            6: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[4, 0, 1]],
            },
            27: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[10, 0, 1]],
            },
            28: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[10, 0, 1]],
            },
            29: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[10, 0, 1]],
            },
            30: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[10, 0, 1]],
            },
        }
    ]
    for grid_key, intersect_dict in example_bridge.global_line_int_dict[0].items():
        assert grid_key in ref_answer[0].keys()  # check keys is correct

        for intersect_type, grid_val in intersect_dict.items():
            # check values
            if grid_val:
                assert grid_val[0] == pytest.approx(
                    ref_answer[0][grid_key][intersect_type][0]
                )


def test_line_load_coincide_transverse_member(bridge_42_0_angle_mesh):
    example_bridge = bridge_42_0_angle_mesh
    # og.opsplt.plot_model("nodes")

    # create reference line load

    barrierpoint_1 = og.create_load_vertex(x=7.5, y=0, z=1, p=2)
    # barrierpoint_1 = og.create_load_vertices(x=7.5, y=0, z=1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=7.5, y=0, z=6, p=2)
    Barrier = og.create_load(
        loadtype="line",
        name="Barrier curb load",
        point1=barrierpoint_1,
        point2=barrierpoint_2,
        shape_function="hermite",
    )
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)
    ref_answer = [
        "ops.load(51, *[0, 0.0, 0, 0, 0, 0])\n",
        "ops.load(30, *[0, 0.0, 0, 0, 0, 0])\n",
        "ops.load(31, *[0, 0.0, 0, 0, 0, 0])\n",
        "ops.load(52, *[0, 0.0, 0, 0, 0, 0])\n",
        "ops.load(51, *[0, 1.2499999999999993, 0, 0, 0, 0])\n",
        "ops.load(30, *[0, 1.3877787807814452e-16, 0, 0, 0, 0])\n",
        "ops.load(31, *[0, 1.3877787807814462e-16, 0, 0, 0, 0])\n",
        "ops.load(52, *[0, 1.2500000000000002, 0, 0, 0, 0])\n",
        "ops.load(52, *[0, 1.2500000000000009, 0, 0, 0, 0])\n",
        "ops.load(31, *[0, -4.163336342344338e-16, 0, 0, 0, 0])\n",
        "ops.load(32, *[0, -4.1633363423443365e-16, 0, 0, 0, 0])\n",
        "ops.load(53, *[0, 1.2500000000000002, 0, 0, 0, 0])\n",
        "ops.load(53, *[0, 1.2500000000000009, 0, 0, 0, 0])\n",
        "ops.load(32, *[0, -4.163336342344338e-16, 0, 0, 0, 0])\n",
        "ops.load(33, *[0, -4.1633363423443365e-16, 0, 0, 0, 0])\n",
        "ops.load(54, *[0, 1.2500000000000002, 0, 0, 0, 0])\n",
        "ops.load(54, *[0, 1.2500000000000024, 0, 0, 0, 0])\n",
        "ops.load(33, *[0, -4.163336342344343e-16, 0, 0, 0, 0])\n",
        "ops.load(34, *[0, -4.163336342344331e-16, 0, 0, 0, 0])\n",
        "ops.load(55, *[0, 1.2499999999999987, 0, 0, 0, 0])\n",
        "ops.load(55, *[0, 0.0, 0, 0, 0, 0])\n",
        "ops.load(34, *[0, -0.0, 0, 0, 0, 0])\n",
        "ops.load(35, *[0, -0.0, 0, 0, 0, 0])\n",
        "ops.load(56, *[0, 0.0, 0, 0, 0, 0])\n",
    ]

    for i, load_command in enumerate(example_bridge.load_case_list[0]["load_command"]):
        start = load_command.find("[")
        end = load_command.find("]")
        pos = eval(load_command[start : (end + 1)])
        start_ref = ref_answer[i].find("[")
        end_ref = ref_answer[i].find("]")
        pos_ref = eval(ref_answer[i][start_ref : (end_ref + 1)])
        assert pos == pytest.approx(pos_ref)


def test_line_load_coincide_edge_beam(bridge_model_42_negative):
    # when set line load z coordinate to z = 0 , test if line returns correct coincide node lines

    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=5, y=0, z=1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=1, p=2)
    Barrier = og.create_load(
        loadtype="line",
        name="Barrier curb load",
        point1=barrierpoint_1,
        point2=barrierpoint_2,
        shape_function="hermite",
    )
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    ref_ans = [
        {
            9: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[5, 0, 1]],
            },
            10: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[5, 0, 1]],
            },
            27: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[10, 0, 1]],
            },
            28: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[10, 0, 1]],
            },
            29: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[10, 0, 1]],
            },
            30: {
                "long_intersect": [],
                "trans_intersect": [],
                "edge_intersect": [],
                "ends": [[10, 0, 1]],
            },
        }
    ]

    for grid_key, intersect_dict in example_bridge.global_line_int_dict[0].items():
        assert grid_key in ref_ans[0].keys()  # check keys is correct

        for intersect_type, grid_val in intersect_dict.items():
            # check values
            if grid_val:
                assert grid_val[0] == pytest.approx(
                    ref_ans[0][grid_key][intersect_type][0]
                )


def test_line_load_outside_of_mesh(bridge_model_42_negative):
    # when set line load z coordinate to z = 0 , test if line returns correct coincide node lines
    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=3, y=0, z=-1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=-1, p=2)
    Barrier = og.create_load(
        loadtype="line",
        point1=barrierpoint_1,
        point2=barrierpoint_2,
        shape_function="hermite",
    )
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)
    assert example_bridge.global_line_int_dict == [{}]


# test a default patch load - patch is within the mesh and sufficiently larger than a single grid
def test_patch_load(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative

    lane_point_1 = og.create_load_vertex(x=5, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=8, z=3, p=5)
    lane_point_3 = og.create_load_vertex(x=8, z=5, p=5)
    lane_point_4 = og.create_load_vertex(x=5, z=5, p=5)
    Lane = og.create_load(
        loadtype="patch",
        point1=lane_point_1,
        point2=lane_point_2,
        point3=lane_point_3,
        point4=lane_point_4,
        shape_function="hermite",
    )
    ULS_DL = og.create_load_case(name="Lane")
    ULS_DL.add_load(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze()

    ref_answer = [
        "ops.load(19, *[0, 1.4068813192153762, 0, 0.7034406596076881, 0, 0.7034406596076881])\n",
        "ops.load(25, *[0, 1.4068813192153762, 0, 0.7034406596076881, 0, -0.7034406596076881])\n",
        "ops.load(26, *[0, 1.4068813192153762, 0, -0.7034406596076881, 0, -0.7034406596076881])\n",
        "ops.load(20, *[0, 1.4068813192153762, 0, -0.7034406596076881, 0, 0.7034406596076881])\n",
        "ops.load(25, *[0, 1.4442076913730961, 0, 0.7221038456865481, 0, 0.7221038456865481])\n",
        "ops.load(60, *[0, 1.4442076913730961, 0, 0.7221038456865481, 0, -0.7221038456865481])\n",
        "ops.load(61, *[0, 1.4442076913730961, 0, -0.7221038456865481, 0, -0.7221038456865481])\n",
        "ops.load(26, *[0, 1.4442076913730961, 0, -0.7221038456865481, 0, 0.7221038456865481])\n",
        "ops.load(13, *[0, 0.00883644799442324, 0, 0.0054378141504143, 0, 0.005492412044427657])\n",
        "ops.load(18, *[0, 0.09579386111020773, 0, 0.05895006837551243, 0, -0.025230076869609933])\n",
        "ops.load(19, *[0, 0.82530095725717, 0, -0.235800273502049, 0, -0.21736681610740755])\n",
        "ops.load(14, *[0, 0.07612939810579983, 0, -0.02175125660165713, 0, 0.04731924222891496])\n",
        "ops.load(18, *[0, 0.11705252575871955, 0, 0.0720323235438274, 0, 0.05852626287935976])\n",
        "ops.load(24, *[0, 0.11705252575871945, 0, 0.07203232354382733, 0, -0.05852626287935973])\n",
        "ops.load(25, *[0, 1.0084525296135802, 0, -0.28812929417530886, 0, -0.5042262648067901])\n",
        "ops.load(19, *[0, 1.0084525296135811, 0, -0.28812929417530914, 0, 0.5042262648067904])\n",
        "ops.load(24, *[0, 0.12015807992224165, 0, 0.07394343379830252, 0, 0.06007903996112076])\n",
        "ops.load(59, *[0, 0.12015807992224087, 0, 0.07394343379830204, 0, -0.06007903996112049])\n",
        "ops.load(60, *[0, 1.035208073176227, 0, -0.2957737351932079, 0, -0.517604036588114])\n",
        "ops.load(25, *[0, 1.0352080731762336, 0, -0.2957737351932098, 0, 0.5176040365881163])\n",
        "ops.load(59, *[0, 0.12494235320970869, 0, 0.07688760197520536, 0, 0.056897774410875845])\n",
        "ops.load(66, *[0, 0.07600612632374003, 0, 0.04677300081460926, 0, -0.040880164010709555])\n",
        "ops.load(67, *[0, 0.6548220114045306, 0, -0.1870920032584372, 0, -0.35219833609226747])\n",
        "ops.load(60, *[0, 1.0764264276528765, 0, -0.3075504079008217, 0, 0.490196210309085])\n",
        "ops.load(60, *[0, 1.501710976078226, 0, 0.750855488039113, 0, 0.6838674808999481])\n",
        "ops.load(67, *[0, 0.9135351721603328, 0, 0.4567675860801664, 0, -0.4913481251287184])\n",
        "ops.load(68, *[0, 0.9135351721603329, 0, -0.45676758608016643, 0, -0.49134812512871845])\n",
        "ops.load(61, *[0, 1.5017109760782261, 0, -0.7508554880391131, 0, 0.6838674808999482])\n",
        "ops.load(61, *[0, 0.5838652274992154, 0, 0.09731087124986965, 0, 0.2658876765739])\n",
        "ops.load(68, *[0, 0.35518247493593585, 0, 0.059197079155989554, 0, -0.1910361510500451])\n",
        "ops.load(69, *[0, 0.01023159392819577, 0, -0.006577453239554427, 0, -0.005503099001441673])\n",
        "ops.load(62, *[0, 0.016819162932076304, 0, -0.010812319027763346, 0, 0.007659315786079486])\n",
        "ops.load(15, *[0, 0.08992923272602986, 0, 0.0, 0, 0.0])\n",
        "ops.load(20, *[0, 0.36279806628438993, 0, 0.0, 0, 0.0])\n",
        "ops.load(21, *[0, 0.05030303322337963, 0, 0.0, 0, 0.0])\n",
        "ops.load(20, *[0, 0.5469954569109332, 0, 0.09116590948515592, 0, 0.2734977284554662])\n",
        "ops.load(26, *[0, 0.5469954569109291, 0, 0.09116590948515522, 0, -0.2734977284554649])\n",
        "ops.load(27, *[0, 0.01575707077521208, 0, -0.010129545498350628, 0, -0.007878535387606049])\n",
        "ops.load(21, *[0, 0.015757070775212195, 0, -0.010129545498350706, 0, 0.007878535387606089])\n",
        "ops.load(26, *[0, 0.5615079504058634, 0, 0.09358465840097817, 0, 0.2807539752029313])\n",
        "ops.load(61, *[0, 0.5615079504058589, 0, 0.09358465840097742, 0, -0.28075397520292983])\n",
        "ops.load(62, *[0, 0.01617512614337903, 0, -0.010398295377886516, 0, -0.008087563071689525])\n",
        "ops.load(27, *[0, 0.016175126143379157, 0, -0.0103982953778866, 0, 0.008087563071689568])\n",
        "ops.load(14, *[0, 0.10620730762527882, 0, 0.05310365381263941, 0, 0.06601456784167825])\n",
        "ops.load(19, *[0, 1.1513685229592219, 0, 0.575684261479611, 0, -0.3032461162212718])\n",
        "ops.load(20, *[0, 1.1513685229592223, 0, -0.5756842614796112, 0, -0.3032461162212719])\n",
        "ops.load(15, *[0, 0.10620730762527884, 0, -0.05310365381263942, 0, 0.06601456784167829])\n",
    ]

    for i, load_command in enumerate(example_bridge.load_case_list[0]["load_command"]):
        start = load_command.find("[")
        end = load_command.find("]")
        pos = eval(load_command[start : (end + 1)])
        start_ref = ref_answer[i].find("[")
        end_ref = ref_answer[i].find("]")
        pos_ref = eval(ref_answer[i][start_ref : (end_ref + 1)])
        assert pos == pytest.approx(pos_ref)  # check each pos


# test for patch load with linear shape function for load distribution
def test_patch_load_using_linear_shape_function(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative

    lane_point_1 = og.create_load_vertex(x=5, y=0, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=8, y=0, z=3, p=5)
    lane_point_3 = og.create_load_vertex(x=8, y=0, z=5, p=5)
    lane_point_4 = og.create_load_vertex(x=5, y=0, z=5, p=5)
    Lane = og.create_load(
        loadtype="patch",
        point1=lane_point_1,
        point2=lane_point_2,
        point3=lane_point_3,
        point4=lane_point_4,
        shape_function="linear",
    )
    ULS_DL = og.LoadCase(name="Lane")
    ULS_DL.add_load(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze()
    ref_answer = [
        "ops.load(19, *[0, 1.4068813192153762, 0, 0, 0, 0])\n",
        "ops.load(25, *[0, 1.4068813192153762, 0, 0, 0, 0])\n",
        "ops.load(26, *[0, 1.4068813192153762, 0, 0, 0, 0])\n",
        "ops.load(20, *[0, 1.4068813192153762, 0, 0, 0, 0])\n",
        "ops.load(25, *[0, 1.4442076913730961, 0, 0, 0, 0])\n",
        "ops.load(60, *[0, 1.4442076913730961, 0, 0, 0, 0])\n",
        "ops.load(61, *[0, 1.4442076913730961, 0, 0, 0, 0])\n",
        "ops.load(26, *[0, 1.4442076913730961, 0, 0, 0, 0])\n",
        "ops.load(13, *[0, 0.03597169309041219, 0, 0, 0, 0])\n",
        "ops.load(18, *[0, 0.16524043980310846, 0, 0, 0, 0])\n",
        "ops.load(19, *[0, 0.6609617592124317, 0, 0, 0, 0])\n",
        "ops.load(14, *[0, 0.14388677236164832, 0, 0, 0, 0])\n",
        "ops.load(18, *[0, 0.22510101107446034, 0, 0, 0, 0])\n",
        "ops.load(24, *[0, 0.2251010110744602, 0, 0, 0, 0])\n",
        "ops.load(25, *[0, 0.9004040442978396, 0, 0, 0, 0])\n",
        "ops.load(19, *[0, 0.90040404429784, 0, 0, 0, 0])\n",
        "ops.load(24, *[0, 0.23107323061969504, 0, 0, 0, 0])\n",
        "ops.load(59, *[0, 0.231073230619694, 0, 0, 0, 0])\n",
        "ops.load(60, *[0, 0.924292922478775, 0, 0, 0, 0])\n",
        "ops.load(25, *[0, 0.9242929224787791, 0, 0, 0, 0])\n",
        "ops.load(59, *[0, 0.22487220771081853, 0, 0, 0, 0])\n",
        "ops.load(66, *[0, 0.16156717600735238, 0, 0, 0, 0])\n",
        "ops.load(67, *[0, 0.6462687040294102, 0, 0, 0, 0])\n",
        "ops.load(60, *[0, 0.899488830843275, 0, 0, 0, 0])\n",
        "ops.load(60, *[0, 1.4054512981926113, 0, 0, 0, 0])\n",
        "ops.load(67, *[0, 1.0097948500459475, 0, 0, 0, 0])\n",
        "ops.load(68, *[0, 1.0097948500459475, 0, 0, 0, 0])\n",
        "ops.load(61, *[0, 1.4054512981926115, 0, 0, 0, 0])\n",
        "ops.load(61, *[0, 0.5059624673493407, 0, 0, 0, 0])\n",
        "ops.load(68, *[0, 0.36352614601654004, 0, 0, 0, 0])\n",
        "ops.load(69, *[0, 0.040391794001838004, 0, 0, 0, 0])\n",
        "ops.load(62, *[0, 0.05621805192770482, 0, 0, 0, 0])\n",
        "ops.load(15, *[0, 0.08992923272602986, 0, 0, 0, 0])\n",
        "ops.load(20, *[0, 0.36279806628438993, 0, 0, 0, 0])\n",
        "ops.load(21, *[0, 0.05030303322337963, 0, 0, 0, 0])\n",
        "ops.load(20, *[0, 0.50647727491753, 0, 0, 0, 0])\n",
        "ops.load(26, *[0, 0.5064772749175274, 0, 0, 0, 0])\n",
        "ops.load(27, *[0, 0.05627525276861446, 0, 0, 0, 0])\n",
        "ops.load(21, *[0, 0.056275252768614746, 0, 0, 0, 0])\n",
        "ops.load(26, *[0, 0.5199147688943169, 0, 0, 0, 0])\n",
        "ops.load(61, *[0, 0.5199147688943141, 0, 0, 0, 0])\n",
        "ops.load(62, *[0, 0.05776830765492456, 0, 0, 0, 0])\n",
        "ops.load(27, *[0, 0.05776830765492487, 0, 0, 0, 0])\n",
        "ops.load(14, *[0, 0.2248230818150756, 0, 0, 0, 0])\n",
        "ops.load(19, *[0, 1.032752748769425, 0, 0, 0, 0])\n",
        "ops.load(20, *[0, 1.0327527487694255, 0, 0, 0, 0])\n",
        "ops.load(15, *[0, 0.22482308181507565, 0, 0, 0, 0])\n",
    ]

    for i, load_command in enumerate(example_bridge.load_case_list[0]["load_command"]):
        start = load_command.find("[")
        end = load_command.find("]")
        pos = eval(load_command[start : (end + 1)])
        start_ref = ref_answer[i].find("[")
        end_ref = ref_answer[i].find("]")
        pos_ref = eval(ref_answer[i][start_ref : (end_ref + 1)])
        assert pos == pytest.approx(pos_ref)


def test_local_vs_global_coord_settings():
    location = og.create_load_vertex(x=5, y=0, z=-2, p=20)  # create load point
    local_location = og.create_load_vertex(x=0, y=0, z=0, p=20)
    local_point_load = og.create_load(
        loadtype="point",
        name="single point",
        point1=local_location,
        shape_function="hermite",
    )  # defined for local coordinate
    global_point_load = og.create_load(
        loadtype="point", name="single point", point1=location, shape_function="hermite"
    )  # defined for local coordinate

    M1600_local = og.CompoundLoad("Truck model")
    M1600_local.add_load(
        load_obj=local_point_load
    )  # if local_coord is set, append the local coordinate of the point load
    M1600_local.set_global_coord(og.Point(5, 0, -2))

    M1600_global = og.CompoundLoad("Truck model global")
    M1600_global.add_load(load_obj=global_point_load)
    assert (
        M1600_local.compound_load_obj_list[0].load_point_1
        == M1600_global.compound_load_obj_list[0].load_point_1
    )


# test analysis of moving load case, test pass if no errors are returned
def test_moving_load_case(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = og.create_load(
        loadtype="point",
        name="front wheel",
        point1=og.LoadPoint(2, 0, 2, 50),
        shape_function="hermite",
    )  # Single point load 50 N

    single_path = og.create_moving_path(
        start_point=og.Point(2, 0, 2), end_point=og.Point(4, 0, 3)
    )  # create path object
    move_point = og.create_moving_load(name="single_moving_point")
    move_point.set_path(single_path)
    move_point.add_load(load_obj=front_wheel)
    example_bridge.add_load_case(move_point)

    example_bridge.analyze()
    results = example_bridge.get_results()
    print(results)


# test moving load + basic load case
# test analysis of moving load case, test pass if no errors are returned
def test_moving_load_and_basic_load_together(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=5, y=0, z=1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=1, p=2)
    Barrier = og.create_load(
        loadtype="line",
        name="Barrier curb load",
        point1=barrierpoint_1,
        point2=barrierpoint_2,
        shape_function="hermite",
    )
    barrier_load_case = og.create_load_case(name="Barrier")
    barrier_load_case.add_load(Barrier)  # ch
    example_bridge.add_load_case(barrier_load_case)
    # add moving load case
    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(2, 0, 2, 50), shape_function="hermite"
    )  # Single point load 50 N

    single_path = og.create_moving_path(
        start_point=og.Point(2, 0, 2), end_point=og.Point(4, 0, 3)
    )  # create path object
    move_point = og.create_moving_load(name="single_moving_point")
    move_point.set_path(single_path)
    move_point.add_load(load_obj=front_wheel)
    example_bridge.add_load_case(move_point)

    # example_bridge.analyze(all=True)
    example_bridge.analyze()
    # results = example_bridge.get_results(load_case="single_moving_point")
    results = example_bridge.get_results(
        combinations={"Barrier": 1, "single_moving_point": 2}
    )
    print(results)


# test moving compound load, test pass if no errors are returned
def test_moving_compound_load(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    M1600 = og.CompoundLoad("M1600 LM")
    back_wheel = og.create_load(
        loadtype="point",
        name="single point",
        point1=og.LoadPoint(5, 0, 2, 20),
        shape_function="hermite",
    )  # Single point load 20 N
    front_wheel = og.create_load(
        loadtype="point",
        name="front wheel",
        point1=og.LoadPoint(2, 0, 2, 50),
        shape_function="hermite",
    )  # Single point load 50 N
    # compound the point loads
    M1600.add_load(load_obj=back_wheel)
    M1600.add_load(load_obj=front_wheel)
    M1600.set_global_coord(og.Point(0, 0, 0))

    truck = og.create_moving_load(name="Truck 1")
    single_path = og.create_moving_path(
        start_point=og.Point(2, 0, 2), end_point=og.Point(4, 0, 2)
    )  # Path object
    truck.set_path(path_obj=single_path)
    truck.add_load(load_obj=M1600)

    example_bridge.add_load_case(truck)
    example_bridge.analyze()
    results = example_bridge.get_results()
    print(results)
    print("finish test compound moving load")


# checks if patch load is correctly-distributed when patch exceeds the bounds of the grillage
def test_patch_partially_outside_mesh(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    lane_point_1 = og.create_load_vertex(x=-5, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=8, z=3, p=5)
    lane_point_3 = og.create_load_vertex(x=8, z=5, p=5)
    lane_point_4 = og.create_load_vertex(x=-5, z=5, p=5)
    Lane = og.create_load(
        loadtype="patch",
        name="Lane 1",
        point1=lane_point_1,
        point2=lane_point_2,
        point3=lane_point_3,
        point4=lane_point_4,
        shape_function="hermite",
    )
    ULS_DL = og.create_load_case(name="Lane")
    ULS_DL.add_load(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze()
    results = example_bridge.get_results()

    ref_answer = [
        "ops.load(10, *[0, 1.1724010993461413, 0, 0.0, 0, 0.0])\n",
        "ops.load(14, *[0, 1.1724010993461444, 0, 0.0, 0, 0.0])\n",
        "ops.load(15, *[0, 1.172401099346146, 0, 0.0, 0, 0.0])\n",
        "ops.load(14, *[0, 1.7586016490192202, 0, 0.8793008245096101, 0, 0.8793008245096101])\n",
        "ops.load(19, *[0, 1.7586016490192202, 0, 0.8793008245096101, 0, -0.8793008245096101])\n",
        "ops.load(20, *[0, 1.7586016490192202, 0, -0.8793008245096101, 0, -0.8793008245096101])\n",
        "ops.load(15, *[0, 1.7586016490192202, 0, -0.8793008245096101, 0, 0.8793008245096101])\n",
        "ops.load(19, *[0, 1.4068813192153762, 0, 0.7034406596076881, 0, 0.7034406596076881])\n",
        "ops.load(25, *[0, 1.4068813192153762, 0, 0.7034406596076881, 0, -0.7034406596076881])\n",
        "ops.load(26, *[0, 1.4068813192153762, 0, -0.7034406596076881, 0, -0.7034406596076881])\n",
        "ops.load(20, *[0, 1.4068813192153762, 0, -0.7034406596076881, 0, 0.7034406596076881])\n",
        "ops.load(25, *[0, 1.4442076913730961, 0, 0.7221038456865481, 0, 0.7221038456865481])\n",
        "ops.load(60, *[0, 1.4442076913730961, 0, 0.7221038456865481, 0, -0.7221038456865481])\n",
        "ops.load(61, *[0, 1.4442076913730961, 0, -0.7221038456865481, 0, -0.7221038456865481])\n",
        "ops.load(26, *[0, 1.4442076913730961, 0, -0.7221038456865481, 0, 0.7221038456865481])\n",
        "ops.load(6, *[0, 0.07503367035815302, 0, 0.0, 0, 0.0])\n",
        "ops.load(9, *[0, 0.07503367035815302, 0, 0.0, 0, 0.0])\n",
        "ops.load(10, *[0, 0.41268518696984174, 0, 0.0, 0, 0.0])\n",
        "ops.load(9, *[0, 0.14631565719839912, 0, 0.09004040442978405, 0, 0.07315782859919957])\n",
        "ops.load(13, *[0, 0.1463156571983994, 0, 0.09004040442978421, 0, -0.07315782859919967])\n",
        "ops.load(14, *[0, 1.2605656620169758, 0, -0.3601616177191363, 0, -0.6302828310084878])\n",
        "ops.load(10, *[0, 1.2605656620169736, 0, -0.3601616177191357, 0, 0.630282831008487])\n",
        "ops.load(13, *[0, 0.14631565719839917, 0, 0.09004040442978412, 0, 0.0731578285991996])\n",
        "ops.load(18, *[0, 0.1463156571983993, 0, 0.09004040442978421, 0, -0.07315782859919966])\n",
        "ops.load(19, *[0, 1.2605656620169776, 0, -0.3601616177191365, 0, -0.6302828310084888])\n",
        "ops.load(14, *[0, 1.2605656620169763, 0, -0.36016161771913613, 0, 0.6302828310084883])\n",
        "ops.load(18, *[0, 0.1170525257587192, 0, 0.07203232354382717, 0, 0.05852626287935966])\n",
        "ops.load(24, *[0, 0.11705252575871981, 0, 0.07203232354382755, 0, -0.05852626287935985])\n",
        "ops.load(25, *[0, 1.0084525296135833, 0, -0.28812929417530975, 0, -0.5042262648067912])\n",
        "ops.load(19, *[0, 1.008452529613578, 0, -0.28812929417530825, 0, 0.5042262648067894])\n",
        "ops.load(24, *[0, 0.12015807992224022, 0, 0.07394343379830169, 0, 0.06007903996112021])\n",
        "ops.load(59, *[0, 0.1201580799222415, 0, 0.07394343379830248, 0, -0.06007903996112065])\n",
        "ops.load(60, *[0, 1.035208073176236, 0, -0.2957737351932102, 0, -0.5176040365881172])\n",
        "ops.load(25, *[0, 1.0352080731762252, 0, -0.295773735193207, 0, 0.5176040365881135])\n",
        "ops.load(59, *[0, 0.12494235320970869, 0, 0.07688760197520536, 0, 0.056897774410875845])\n",
        "ops.load(66, *[0, 0.07600612632374003, 0, 0.04677300081460926, 0, -0.040880164010709555])\n",
        "ops.load(67, *[0, 0.6548220114045306, 0, -0.1870920032584372, 0, -0.35219833609226747])\n",
        "ops.load(60, *[0, 1.0764264276528765, 0, -0.3075504079008217, 0, 0.490196210309085])\n",
        "ops.load(60, *[0, 1.501710976078218, 0, 0.7508554880391092, 0, 0.6838674808999459])\n",
        "ops.load(67, *[0, 0.9135351721603383, 0, 0.4567675860801694, 0, -0.4913481251287209])\n",
        "ops.load(68, *[0, 0.9135351721603405, 0, -0.45676758608017004, 0, -0.49134812512872195])\n",
        "ops.load(61, *[0, 1.501710976078221, 0, -0.7508554880391103, 0, 0.6838674808999475])\n",
        "ops.load(61, *[0, 0.5838652274992154, 0, 0.09731087124986965, 0, 0.2658876765739])\n",
        "ops.load(68, *[0, 0.35518247493593585, 0, 0.059197079155989554, 0, -0.19103615105004512])\n",
        "ops.load(69, *[0, 0.01023159392819577, 0, -0.006577453239554427, 0, -0.005503099001441674])\n",
        "ops.load(62, *[0, 0.016819162932076304, 0, -0.010812319027763346, 0, 0.007659315786079486])\n",
        "ops.load(15, *[0, 0.5697869342822274, 0, 0.0, 0, 0.0])\n",
        "ops.load(20, *[0, 0.5697869342822279, 0, 0.0, 0, 0.0])\n",
        "ops.load(21, *[0, 0.12661931872938303, 0, 0.0, 0, 0.0])\n",
        "ops.load(20, *[0, 0.5469954569109349, 0, 0.09116590948515615, 0, 0.2734977284554669])\n",
        "ops.load(26, *[0, 0.5469954569109275, 0, 0.09116590948515492, 0, -0.27349772845546444])\n",
        "ops.load(27, *[0, 0.015757070775212, 0, -0.010129545498350583, 0, -0.007878535387606017])\n",
        "ops.load(21, *[0, 0.015757070775212212, 0, -0.01012954549835072, 0, 0.007878535387606089])\n",
        "ops.load(26, *[0, 0.5615079504058634, 0, 0.09358465840097817, 0, 0.2807539752029313])\n",
        "ops.load(61, *[0, 0.5615079504058589, 0, 0.09358465840097742, 0, -0.28075397520292983])\n",
        "ops.load(62, *[0, 0.01617512614337903, 0, -0.010398295377886516, 0, -0.008087563071689525])\n",
        "ops.load(27, *[0, 0.016175126143379157, 0, -0.0103982953778866, 0, 0.008087563071689568])\n",
    ]

    for i, load_command in enumerate(example_bridge.load_case_list[0]["load_command"]):
        start = load_command.find("[")
        end = load_command.find("]")
        pos = eval(load_command[start : (end + 1)])
        start_ref = ref_answer[i].find("[")
        end_ref = ref_answer[i].find("]")
        pos_ref = eval(ref_answer[i][start_ref : (end_ref + 1)])
        assert pos == pytest.approx(pos_ref)


def test_clearing_results(bridge_model_42_negative):
    # test functionality of clearing load case after analysis
    example_bridge = bridge_model_42_negative
    lane_point_1 = og.create_load_vertex(x=-5, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=8, z=3, p=5)
    lane_point_3 = og.create_load_vertex(x=8, z=5, p=5)
    lane_point_4 = og.create_load_vertex(x=-5, z=5, p=5)
    Lane = og.create_load(
        loadtype="patch",
        name="Lane 1",
        point1=lane_point_1,
        point2=lane_point_2,
        point3=lane_point_3,
        point4=lane_point_4,
        shape_function="hermite",
    )
    ULS_DL = og.create_load_case(name="Lane")
    ULS_DL.add_load(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze()
    results = example_bridge.get_results()
    assert example_bridge.results.basic_load_case_record != {}
    assert example_bridge.load_case_list != []
    example_bridge.clear_load_cases(load_case="Lane")
    assert example_bridge.results.basic_load_case_record == {}
    assert example_bridge.load_case_list == []


def test_load_analysis_shell_model(shell_link_bridge):
    # checks a benchmark analysis on a shell_beam model
    shell_link_model = shell_link_bridge
    # og.opsplt.plot_model("nodes")

    lane_point_1 = og.create_load_vertex(x=5, y=0, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=8, y=0, z=3, p=5)
    lane_point_3 = og.create_load_vertex(x=8, y=0, z=5, p=5)
    lane_point_4 = og.create_load_vertex(x=5, y=0, z=5, p=5)
    Lane = og.PatchLoading(
        point1=lane_point_1,
        point2=lane_point_2,
        point3=lane_point_3,
        point4=lane_point_4,
    )
    ULS_DL = og.LoadCase(name="Lane")
    ULS_DL.add_load(Lane)  # ch
    shell_link_model.add_load_case(ULS_DL)
    shell_link_model.analyze()

    results = shell_link_model.get_results()
    print(results)


def test_load_analysis_shell_multi_span(ref_bridge_properties):
    # checks integration of load analysis with multi - span feature + shell beam model
    def create_multispan_shell_model(ref_bridge_properties):
        # creates a reference shell beam model
        I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

        # Adopted units: N and m
        kilo = 1e3
        milli = 1e-3
        m = 1
        m2 = m**2
        m3 = m**3
        m4 = m**4

        # parameters of bridge grillage
        L = 30 * m  # span
        w = 10 * m  # width
        n_l = 7  # number of longitudinal members
        n_t = 11  # number of transverse members
        edge_dist = 1.05 * m  # distance between edge beam and first exterior beam
        bridge_name = "multi span showcase"
        angle = 20  # degree
        mesh_type = "Oblique"
        model_type = "shell_beam"
        # multispan specific vars
        spans = [9 * m, 12 * m, 9 * m]
        nl_multi = [20, 10, 20]
        stich_slab_x_spacing = 0.5 * m

        variant_one_model = og.create_grillage(
            bridge_name=bridge_name,
            long_dim=L,
            width=w,
            skew=angle,
            num_long_grid=n_l,
            num_trans_grid=n_t,
            edge_beam_dist=edge_dist,
            mesh_type=mesh_type,
            model_type=model_type,
            multi_span_dist_list=spans,
            multi_span_num_points=nl_multi,
            continuous=False,
            non_cont_spacing_x=stich_slab_x_spacing,
            max_mesh_size_z=1,
            max_mesh_size_x=1,
            offset_beam_y_dist=0.499,
            beam_width=0.89,
        )

        # create material of slab shell
        slab_shell_mat = og.create_material(
            material="concrete", code="AS5100-2017", grade="50MPa", rho=2400
        )

        # create section of slab shell
        slab_shell_section = og.create_section(h=0.2)
        slab_shell = og.create_member(
            section=slab_shell_section, material=slab_shell_mat
        )

        # create stitch slab conencting elements
        stitch_slab_section = og.create_section(
            A=0.504 * m2,
            J=5.22303e-3 * m3,
            Iy=0.32928 * m4,
            Iz=1.3608e-3 * m4,
            Ay=0.42 * m2,
            Az=0.42 * m2,
        )
        stitch_slab = og.create_member(section=stitch_slab_section, material=concrete)

        # set shell
        variant_one_model.set_shell_members(slab_shell)

        # assign grillage member to element groups of grillage model
        variant_one_model.set_member(I_beam, member="interior_main_beam")
        variant_one_model.set_member(I_beam, member="exterior_main_beam_1")
        variant_one_model.set_member(I_beam, member="exterior_main_beam_2")
        variant_one_model.set_member(exterior_I_beam, member="edge_beam")
        # variant_one_model.set_member(stitch_slab, member="stitch_elements")

        variant_one_model.create_osp_model(pyfile=False)

        return variant_one_model

    shell_bridge = create_multispan_shell_model(ref_bridge_properties)

    # create and add load case comprise of single point load
    P = 20e3
    point_load_location = og.create_load_vertex(
        x=4.5, y=0, z=6.5, p=P
    )  # about midspan of span 1
    point_load = og.create_load(
        loadtype="point", name="single point", point1=point_load_location
    )
    point_lc = og.create_load_case(name="pointload")
    point_lc.add_load(point_load)
    shell_bridge.add_load_case(point_lc)
    shell_bridge.analyze()
    # extract results
    result = shell_bridge.get_results()
    print(result)


def test_load_analysis_on_spring_support_single_span(ref_bridge_properties):
    # test multispan feature
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # parameters of bridge grillage
    L = 33.5 * m  # span
    w = 11.565 * m  # width
    n_l = 7  # number of longitudinal members
    n_t = 11  # number of transverse members
    edge_dist = 1.05 * m  # distance between edge beam and first exterior beam
    bridge_name = "multi span showcase"
    angle = 10  # degree
    mesh_type = "Oblique"

    # multispan specific vars
    spans = [9 * m, 12 * m, 9 * m]
    nl_multi = [3, 5, 10]
    stich_slab_x_spacing = 1 * m
    stitch_slab_section = og.create_section(
        A=0.504 * m2,
        J=5.22303e-3 * m3,
        Iy=0.32928 * m4,
        Iz=1.3608e-3 * m4,
        Ay=0.42 * m2,
        Az=0.42 * m2,
    )
    stich_slab = og.create_member(section=stitch_slab_section, material=concrete)

    variant_one_model = og.create_grillage(
        bridge_name=bridge_name,
        long_dim=L,
        width=w,
        skew=angle,
        num_long_grid=n_l,
        num_trans_grid=n_t,
        edge_beam_dist=edge_dist,
        mesh_type=mesh_type,
        multi_span_dist_list=spans,
        multi_span_num_points=nl_multi,
        continuous=True,
        # non_cont_spacing_x=stich_slab_x_spacing,
    )

    # assign grillage member to element groups of grillage model
    variant_one_model.set_member(I_beam, member="interior_main_beam")
    variant_one_model.set_member(I_beam, member="exterior_main_beam_1")
    variant_one_model.set_member(I_beam, member="exterior_main_beam_2")
    variant_one_model.set_member(exterior_I_beam, member="edge_beam")
    variant_one_model.set_member(slab, member="transverse_slab")
    variant_one_model.set_member(slab, member="start_edge")
    variant_one_model.set_member(slab, member="end_edge")
    # variant_one_model.set_member(stich_slab, member="stitch_elements")

    # spring support
    e_spring = 11e13
    variant_one_model.set_spring_support(
        rotational_spring_stiffness=e_spring, edge_num=1
    )

    variant_one_model.create_osp_model(pyfile=False)
    # og.opsplt.plot_model()

    # create and add load case comprise of single point load
    P = 20e3
    point_load_location = og.create_load_vertex(
        x=7.5, y=0, z=3, p=P
    )  # about midspan of span 1
    point_load = og.create_load(name="single point", point1=point_load_location)
    point_lc = og.create_load_case(name="pointload")
    point_lc.add_load(point_load)
    variant_one_model.add_load_case(point_lc)
    variant_one_model.analyze()

    result = variant_one_model.get_results()
    print(result)

    ref_value = result.forces.sel(
        Loadcase="pointload", Component="Mz_i", Element=20
    ).to_numpy()
    assert og.np.isclose(
        ref_value.tolist(),
        0.49505451544913914,
    )


def test_compare_shell_beam_analysis(run_beam_model_point_load):
    # run fixture to get bridges
    beam_bridge, result_beam, shell_bridge, result_shell = run_beam_model_point_load
    beam_bridge.get_element(member="exterior_main_beam_1")
    len(
        result_beam.forces.sel(
            Loadcase="line",
            Element=beam_bridge.get_element(member="exterior_main_beam_1")[0],
        )
    )
    # get middle interior beam results
    og.plot_force(
        beam_bridge, result_beam, member="exterior_main_beam_2", component="Mz"
    )
    og.plot_defo(
        beam_bridge, result_beam, member="exterior_main_beam_1", option="nodes"
    )
    og.plot_defo(
        shell_bridge, result_shell, member="interior_main_beam", option="nodes"
    )
    og.opsv.plot_defo()


def test_transient(beam_element_bridge):
    """A test for the uncoupled transient analysis portion of VBI basic framework"""
    positions = [5, 5, 10, 15]
    P = 100 * kN
    first_step = True
    previous_state = None

    # start moving vehicle through all positions
    for x in positions:
        # create load case
        mid_point_line_loadcase = og.create_load_case(name="VBI")
        lp1 = og.create_load_vertex(x=x, y=0, z=3.5, p=P)
        mid_point_line_load = og.create_load(
            name="unit load",
            point1=lp1,
        )
        mid_point_line_loadcase.add_load(mid_point_line_load)

        # create bridge instance
        beam_bridge = beam_element_bridge
        beam_bridge.create_osp_model()

        print(og.ops.eigen(2))
        og.ops.rayleigh(0.0, 0.0, 0.0, 2 * 0.02 / 4)

        # set previous state
        if not first_step:
            beam_bridge.set_previous_state(previous_state)
        first_step = False

        # add load case, run and store
        beam_bridge.add_load_case(mid_point_line_loadcase)
        beam_bridge.analyze(analysis_type="Transient", step=100, time_increment=0.1)
        previous_state = beam_bridge.store_state()
        result = beam_bridge.get_results()
        print(result)
        postprocessor = og.PostProcessor(beam_bridge, result)

        contactpoints = postprocessor.get_arbitrary_displacements(point=[5, 0, 3.5])
        # do something with results
        print(result)
        print("Next step")
