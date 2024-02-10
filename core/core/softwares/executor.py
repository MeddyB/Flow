import os

import jeanpaulstart


class FlowExecutor(jeanpaulstart.Executor):


    def step(self):
        """
        Applies the next available task
        :return: status, a list of new messages
        """
        self._step_messages()

        if self.status == jeanpaulstart.EXEC_IDLE:
            self._begin()

        if self.has_stopped:
            return self.status

        current_task = self.batch.tasks[self._task_index]
        self._task_index += 1

        status, messages = jeanpaulstart.executor._apply_(current_task)
        self._post_messages(['[{0}]{1}'.format(self.batch.name, message) for message in messages])

        if status == jeanpaulstart.TASK_ERROR_IGNORED:
            self._ignored_errors += 1

        if current_task.register_status and status != jeanpaulstart.TASK_WHEN_FALSE:
            self._registered_status = status
            os.environ[jeanpaulstart.EXEC_REGISTERED_STATUS_ENV_VAR] = str(status)

        if current_task.exit_if_not_ok and status not in (jeanpaulstart.OK, jeanpaulstart.TASK_WHEN_FALSE):
            self._abort(current_task.name, 'Status was not OK and exit_if_not_ok=true')
            return status, self.last_messages

        if self._task_index >= len(self.batch.tasks):
            self._finish()

        return status, self.last_messages
