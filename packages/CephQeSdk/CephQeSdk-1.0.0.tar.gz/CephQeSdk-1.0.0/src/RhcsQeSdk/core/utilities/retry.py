import logging
import time

import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RetryMixin:
    def __init__(self):
        pass

    def compare_result_with_args(self, output, args):
        """
        compare output with the arguments and returns output matches or not.
        Args:
          output(dict): results of all ip's.
          args(dict): key val pair that needs to be checked with the output.

        Returns:
          True or False.
        """
        success = True
        for ip, result in output.items():
            out_dict = yaml.safe_load(result)
            out_dict = list(out_dict.values())[0]
            if args.get("value") not in out_dict.get(args.get("key")):
                success = False
                break
        return success

    def dict_check(self, result, args):
        """
        compare result with the arguments and returns output matches or not.
        Args:
          result(dict): result of the command.
          args(dict): key val pair that needs to be checked with the result.

        Returns:
          True or False.
        """
        if not isinstance(result, dict):
            return True
        for key, val in result.items():
            if key == args.get("key"):
                if not val == args.get("val"):
                    return False
            elif not self.dict_check(val, args):
                return False
        return True

    def retry(self, kw):
        success = 0
        runner = kw.get("runner")
        retry_args = kw.get("args")
        interval_seconds = retry_args.get("interval_seconds", 1)
        pattern = retry_args.get("pattern")
        for i in range(retry_args.get("max_attempts", 1)):
            out = runner.run()

            if self.compare_result_with_args(out, pattern):
                success = 1
                break
            time.sleep(interval_seconds)
        if not success:
            logger.info("status not equals to expected even after max attempts")
            return False
        return True
