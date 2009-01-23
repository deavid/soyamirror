import soya
from soya import Body
from soya.sdlconst import KEYDOWN, K_LEFT
from soya.testlib import SoyaTestCase, TestCase, unittest_main


class TaskTC(SoyaTestCase):

    def test_task_call_multiple_time(self):
        input = [1, 3, 6]
        output = []
        def test_task(input=input, output=output):
            output.append(input.pop())

        self.main_loop.round_tasks.append(test_task)

        self.run_soya_rounds()
        self.assertEquals(output, [6])
        self.run_soya_rounds()
        self.assertEquals(output, [6, 3])

    def test_task_call_after_event_before_object(self):
        input = [1, 3, 6]
        output = []
        def test_task(input=input, output=output):
            output.append(input.pop())
            output.append(soya.MAIN_LOOP.events)

        class InputModifier(Body):
            def begin_round(self):
                Body.begin_round(self)
                input.append(42)

        event = (KEYDOWN, K_LEFT, None) # XXX add a valid modifier
        soya.MAIN_LOOP.queue_event(event)

        self.main_loop.round_tasks.append(test_task)

        InputModifier(self.scene)

        self.main_loop.begin_round()
        self.assertEquals(output, [6, [event]])
        self.assertEquals(input,  [1, 3, 42])


if __name__ == '__main__':
    unittest_main()
