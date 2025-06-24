# This file was renamed from utils.py to core_utils.py to avoid import ambiguity with the utils/ package.
# All previous imports from utils import ... should now be from core_utils import ...

import os
import google.generativeai as genai
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any, Union
import re
import streamlit as st
import logging
import json
import csv
from dataclasses import dataclass
from pathlib import Path
import ncc_utils as _ncc_utils

# --- Configuration ---
Config = _ncc_utils.Config

setup_gemini = _ncc_utils.setup_gemini
get_ncc_response = _ncc_utils.get_ncc_response
API_CALL_COOLDOWN_MINUTES = _ncc_utils.API_CALL_COOLDOWN_MINUTES
clear_history = _ncc_utils.clear_history
read_history = _ncc_utils.read_history
clear_quiz_score_history = _ncc_utils.clear_quiz_score_history
_is_in_cooldown = _ncc_utils._is_in_cooldown
_cooldown_message = _ncc_utils._cooldown_message
