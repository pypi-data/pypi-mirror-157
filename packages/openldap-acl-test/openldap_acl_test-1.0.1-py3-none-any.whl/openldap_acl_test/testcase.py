import subprocess
from enum import Enum
from logging import getLogger

from openldap_acl_test import __name__
from openldap_acl_test.exceptions import ACLCheckError, ACLNoCheckAttributeError

logger = getLogger(__name__)


class ACL(str, Enum):
    MANAGE = "manage"
    WRITE = "write"
    READ = "read"
    AUTH = "auth"
    NONE = "none"


class ACLTestResult:
    """
    テストケースの検証結果を保持するクラス
    """

    def __init__(self, result: bool = True, msg: str = ""):
        self.result = result
        self.msg = msg


class ACLTestCase:
    """
    テストケースを保持するクラス
    """

    def __init__(
        self,
        requester: str,
        target: str,
        acl: ACL = ACL.READ,
        attributes: list[str] = None,
    ):
        self.requester = requester
        self.target = target
        self.acl = acl
        if attributes is None:
            attributes = []
        self.attributes: list[str] = attributes
        self.result_list: list[ACLTestResult] = []

    def run_test(self, slapacl: str = "/usr/sbin/slapacl"):
        """
        slapaclを実行する関数

        適切にslapaclコマンドを呼び出しその出力からACLを検証する。
        検証結果はself.result_listに記録される。

        :param str slapacl: slapaclコマンドのパス
        """
        args = self.get_slapacl_args()
        cmd = [slapacl] + args

        logger.debug(f"RUN COMMAND [{' '.join(cmd)}]")
        res = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10, check=True
        )
        for line in res.stderr.split("\n"):
            if len(line.strip()) == 0:
                continue
            if line.startswith("authcDN"):
                continue
            try:
                msg = self.check_slapacl(line)
                logger.debug(f"[OK] {msg}")
                self.result_list.append(ACLTestResult(True, msg))
            except ACLNoCheckAttributeError as error:
                logger.debug(f"[WARN] {error}")
                continue

            except ACLCheckError as error:
                logger.error(f"[ERROR] {error}")
                self.result_list.append(ACLTestResult(False, str(error)))
            except Exception as error:
                logger.error(f"[UNKNOWN ERROR] {error}")
                self.result_list.append(ACLTestResult(False, str(error)))

    def get_slapacl_args(self) -> list[str]:
        """
        slapaclに与えるべき引数を取得する。

        :return: slapaclコマンドの引数
        :rtype: list[str]
        """
        requester = self.requester
        if self.requester == "self":
            requester = self.target
        args: list[str] = []
        if requester != "anonymous":
            args += ["-D", requester]
        args += ["-b", self.target]
        attribute_args: list[str] = []
        for attribute in self.attributes:
            if self.acl != ACL.NONE:
                attribute_args.append(f"{attribute}/{self.acl}")
            else:
                # noneでは attr/access の記述が出来ない
                attribute_args.append(attribute)
        args += attribute_args
        return args

    def check_slapacl(self, line: str) -> str:
        """
        slapaclの出力行をみて、検証結果を判断する関数

        slapaclの出力行をみ、対応する属性の検証結果を返す。
        検証に成功した場合はその旨のメッセージを返す。
        検証に失敗した場合はACLCheckErrorをraiseする。

        slapaclの出力例はnoneの検証かそれ以外かで変わる。

        * slapaclの出力例 (userPassowr/auth 検証成功)

        ```
        auth access to userPassword: ALLOWED
        ```

        * slapaclの出力例 (userPassowr/write 検証失敗)

        ```
        write access to userPassword: DENIED
        ```

        * slapaclの出力例 (sn none検証成功)

        ```
        sn: none(=0)
        ```

        * slapaclの出力例 (sn none検証失敗)

        ```
        sn: read(=rscxd)
        ```

        :param str line: slapaclの出力行
        :return: slapaclの検証結果
        :rtype: str
        :raises: ACLCheckError
        """
        line = line.strip()
        parts = line.split(": ")
        if len(parts) != 2:
            raise ACLCheckError(f"Invalid output [{line}]")

        if self.acl == ACL.NONE:
            return self._check_slapacl_none(parts[0], parts[1])
        else:
            return self._check_slapacl(parts[0], parts[1])

    def _check_slapacl(self, before_text, after_text) -> str:
        attribute = before_text.split(" ")[-1]
        if attribute not in self.attributes:
            raise ACLNoCheckAttributeError(f"No check attribute [{attribute}]")

        acl = before_text.split(" ")[0]
        if acl != self.acl:
            raise ACLCheckError(f"ACL not match [{acl} (expected {self.acl})]")

        if after_text == "ALLOWED":
            return f"{attribute} check success!"
        raise ACLCheckError(f"{attribute}/{self.acl} check failure")

    def _check_slapacl_none(self, before_text, after_text) -> str:
        attribute = before_text
        if attribute not in self.attributes:
            raise ACLNoCheckAttributeError(f"No check attribute [{attribute}]")

        if after_text.startswith("none"):
            return f"{attribute} check success!"
        raise ACLCheckError(f"{attribute}/none check failure. [{after_text}]")

    def get_success_count(self):
        """
        self.result_listの成功数を返す

        :return: self.result_listの成功数
        :rtype: int
        """
        count = 0
        for result in self.result_list:
            if result.result:
                count += 1
        return count

    def get_failure_count(self) -> int:
        """
        self.result_listの失敗数を返す

        :return: self.result_listの失敗数
        :rtype: int
        """
        count = 0
        for result in self.result_list:
            if not result.result:
                count += 1
        return count

    def get_result_dots(self) -> str:
        """
        self.result_listの結果を示すテキストを返す

        pytestをイメージしたテキスト。成功は . 失敗は x で表現する。

        :return: self.result_listの結果
        :rtype: str
        """
        text = ""
        for result in self.result_list:
            if result.result:
                text += "."
            else:
                text += "x"
        return text
