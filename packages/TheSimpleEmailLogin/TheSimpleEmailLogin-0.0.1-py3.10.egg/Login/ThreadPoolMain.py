import os.path
import threading
import time
import click
from concurrent.futures import ProcessPoolExecutor

from Login.ProtocolLogin.LoginHandler import LoginHandler
from Login.Input.LoginInfoLoader import LoginInfoLoader
from Login.Output.ResultOutput import ResultOutput

lock = threading.Lock()


def doLogin(loginInfo):
    email = loginInfo[0]
    pwd = loginInfo[1]
    results = LoginHandler.findConfigAndLogin(email, pwd)
    return results


def when_done(r):
    lock.acquire()
    resultList = r.result()
    for result in resultList:
        resultString = ' '.join(map(str, result))
        if result[0]:
            ResultOutput.outputSucceedResult(resultString + '\n')
        else:
            ResultOutput.outputFailedResult(resultString + '\n')
        print(resultString)
    lock.release()


@click.command()
@click.option('-s', '--string', type=str)
def clickLogin(string):
    login(string)


def login(p):
    if len(p) == 0:
        click.echo("empty file path " + p, err=True)
        return

    if not os.path.exists(p):
        click.echo("invalid file path " + p, err=True)
        return

    click.echo('开始尝试登录')
    begin = time.time()

    # 切换工作路径
    fileFolderPath = os.path.dirname(p)
    if os.path.exists(fileFolderPath) and os.getcwd() != fileFolderPath:
        os.chdir(fileFolderPath)

    # 解析文件里的账号密码
    loginInfoArray = LoginInfoLoader.loadLoginInfoArray(p)
    if len(loginInfoArray) == 0:
        click.echo("empty login info" + p, err=True)
        return

    # 创建结果文件
    fileName = os.path.basename(p).split('.')[0]

    succeedResultFileName = 'succeed_result_' + fileName + '.txt'
    failedResultFileName = 'failed_result_' + fileName + '.txt'
    ResultOutput.openSucceedFile(succeedResultFileName)
    ResultOutput.openFailedFile(failedResultFileName)

    # 执行登录行为
    with ProcessPoolExecutor(max_workers=60) as pool:
        for loginInfo in loginInfoArray:
            future_result = pool.submit(doLogin, loginInfo)
            future_result.add_done_callback(when_done)

    ResultOutput.closeSucceedFile()
    ResultOutput.closeFailedFile()

    end = time.time()
    print("登录完成，总耗时", end - begin)

if __name__ == '__main__':
    login('asdasdasd')

