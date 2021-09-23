"""
    Copyright (c) 2021 Fedora Websites and Apps

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import click
from fedora_easyfix.__init__ import __version__
from fedora_easyfix.utilities.consumer import (
    ErraticReturns,
    TicketDataRetrieval,
)
from flask import Flask, jsonify, render_template, request

main = Flask(__name__)


@main.get("/0/preliminary/")
def return_preliminary_information():
    try:
        return_data = TicketDataRetrieval().retrieve_preliminary_information()
    except FileNotFoundError as expt:
        return_data = ErraticReturns().file_read_error_return_data()
    return jsonify(return_data)


@main.get("/0/forges/")
def return_forge_list():
    try:
        return_data = TicketDataRetrieval().retrieve_forge_list()
    except FileNotFoundError as expt:
        return_data = ErraticReturns().file_read_error_return_data()
    return jsonify(return_data)


@main.get("/0/forges/<string:forge>/")
def return_forge_information(forge):
    try:
        return_data = TicketDataRetrieval().retrieve_forge_information(forge)
    except FileNotFoundError as expt:
        return_data = ErraticReturns().file_read_error_return_data()
    return jsonify(return_data)


@main.get("/0/forges/<string:forge>/repositories/")
def return_repository_list(forge):
    try:
        return_data = TicketDataRetrieval().retrieve_repository_list(forge)
    except FileNotFoundError as expt:
        return_data = ErraticReturns().file_read_error_return_data()
    return jsonify(return_data)


@main.get("/0/forges/<string:forge>/repositories/<path:repository>/")
def return_repository_information(forge, repository):
    try:
        return_data = TicketDataRetrieval().retrieve_repository_information(forge, repository)
    except FileNotFoundError as expt:
        return_data = ErraticReturns().file_read_error_return_data()
    return jsonify(return_data)


@main.get("/0/forges/<string:forge>/repositories/<path:repository>/issues/")
def return_issue_list(forge, repository):
    try:
        return_data = TicketDataRetrieval().retrieve_issue_list(forge, repository)
    except FileNotFoundError as expt:
        return_data = ErraticReturns().file_read_error_return_data()
    return jsonify(return_data)


@main.get("/0/forges/<string:forge>/repositories/<path:repository>/issues/<string:number>/")
def return_issue_information(forge, repository, number):
    try:
        return_data = TicketDataRetrieval().retrieve_issue_information(forge, repository, number)
    except FileNotFoundError as expt:
        return_data = ErraticReturns().file_read_error_return_data()
    return jsonify(return_data)


@main.get("/")
def mainpage():
    return render_template("mainpage.html")


@click.command()
@click.option("-p", "--portdata", "portdata", help="Set the port value [0-65536]", default="9696")
@click.option("-6", "--ipprotv6", "netprotc", flag_value="ipprotv6", help="Start the server on an IPv6 address")
@click.option("-4", "--ipprotv4", "netprotc", flag_value="ipprotv4", help="Start the server on an IPv4 address")
@click.version_option(version=__version__, prog_name="Fedora Easyfix")
def mainfunc(portdata, netprotc):
    """
    A collection of self-contained and well-documented issues for newcomers to start contributing with
    """
    print(" * Starting Fedora Easyfix...")
    print(" * Port number : " + str(portdata))
    netpdata = ""
    if netprotc == "ipprotv6":
        print(" * IP version  : 6")
        netpdata = "::"
    elif netprotc == "ipprotv4":
        print(" * IP version  : 4")
        netpdata = "0.0.0.0"
    main.config["TEMPLATES_AUTO_RELOAD"] = True
    main.run(port=portdata, host=netpdata)


if __name__ == "__main__":
    mainfunc()
