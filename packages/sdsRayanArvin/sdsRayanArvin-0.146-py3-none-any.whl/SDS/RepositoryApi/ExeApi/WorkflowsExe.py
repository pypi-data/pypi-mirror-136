from sdsRayanArvin.Repository import Repository


class WorkflowsExe(Repository):
    def ProcessRunOnId(self, ID_process):
        res = self.Request.sendWithToken('GET', 'run/' + ID_process + '/0')
        return res['status']
