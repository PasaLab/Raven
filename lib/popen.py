import subprocess


def subprocess_popen(statement):
    p = subprocess.Popen(statement, shell=True, stdout=subprocess.PIPE)
    while p.poll() is None:
        if p.wait() is not 0:
            print("Failed")
            return False
        else:
            re = p.stdout.readlines()
            result = []
            for i in range(len(re)):
                res = re[i].decode('utf-8').strip('\r\n')
                result.append(res)
            return result