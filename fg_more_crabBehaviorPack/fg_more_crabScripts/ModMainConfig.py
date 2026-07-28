# -*- coding: utf-8 -*-
import json
import logging


IN_DEVELOPMENT = False
DEVELOPMENT_LEVEL = logging.ERROR

ModName = "fg_more_crab"
MOD_VERSION = "1.0.0"

ModScriptFilePath = "%sScripts" % ModName
ServerSystemName = "%sServerSystem" % ModName
ServerSystemClsPath = ModScriptFilePath + ".server.ServerMainSystem.ServerMainSystem"


def SetDevelopmentMessage(level, message, *args):
    if not isinstance(DEVELOPMENT_LEVEL, int) or level < DEVELOPMENT_LEVEL:
        return

    def safe_to_text(value):
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            try:
                return str(value)
            except Exception:
                return "<unserializable>"

    try:
        text_args = tuple(safe_to_text(arg) for arg in args)
        if text_args:
            try:
                message = message % text_args
            except Exception:
                message = "%s | %s" % (message, ", ".join(text_args))
        logging.log(level, "[fg_more_crab] %s" % message)
    except Exception:
        if IN_DEVELOPMENT:
            raise

