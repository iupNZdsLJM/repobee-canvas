# Copyright 2021 Huub de Beer <h.t.d.beer@tue.nl>
#
# Licensed under the EUPL, Version 1.2 or later. You may not use this work
# except in compliance with the EUPL. You may obtain a copy of the EUPL at:
#
# https://joinup.ec.europa.eu/software/page/eupl
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the EUPL is distributed on an "AS IS" basis, WITHOUT
# WARRANTY OR CONDITIONS OF ANY KIND, either express or implied. See the EUPL
# for the specific language governing permissions and limitations under the
# licence.
"""Logging functions for the canvas plugin commands.

Functions:
- inform: Show an informational message.
- warn: Show a warning.
- fault: Show an error message.
"""
import repobee_plug as plug

def warn(msg : str, error : BaseException = None) -> None:
    """Show warning message.
    """
    plug.echo(f"WARNING: {msg}")
    if error:
        plug.echo(f"\t{str(error)}")

def fault(msg : str, error : BaseException = None) -> None:
    """Show error message.
    """
    plug.echo(f"ERROR: {msg}")
    if error:
        plug.echo(f"\t{str(error)}")

def inform(msg : str) -> None:
    """Show informational message.
    """
    plug.echo(msg)
