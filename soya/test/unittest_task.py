from soya.testlib import SoyaTestCase, TestCase, unittest_main


class TaskTC(SoyaTestCase):

    def test_task_call(self):
        input = [1, 3, 6]
        output = []
        def test_task(input=input, output=output):
            output.append(input.pop())

        self.main_loop.round_tasks.append(test_task)

        self.run_soya_rounds()
        self.assertEquals(output, [6])
        self.run_soya_rounds()
        self.assertEquals(output, [6, 3])


if __name__ == '__main__':
    unittest_main()
