# TOFU
# Copyright (C) 2006 Jean-Baptiste LAMY
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# Unit tests for Tofu

#from sides import *
from tofu_udp import *
import unittest


class TestSides(unittest.TestCase):
  def __init__(self, *args, **kargs):
    unittest.TestCase.__init__(self, *args, **kargs)
    
    tester = self
    class MyMobile(Multisided):
      @side("server")
      def client_or_server(self): tester.server_task_done()
      @side("client")
      def client_or_server(self): tester.client_task_done()
      
      @side("server", "client")
      def both_client_server(self):
        tester.server_task_done()
        tester.client_task_done()
        
      @side("server", "client")
      def both_client_server_and_client(self):
        tester.server_task_done()
        tester.client_task_done()
      @side("client")
      def both_client_server_and_client(self): tester.client_task_done()
      
    self.mobile = MyMobile()
    
  def setUp(self):
    self.tasks_done = []
    
  def server_task_done(self): self.tasks_done.append("server")
  def client_task_done(self): self.tasks_done.append("client")
  def single_task_done(self): self.tasks_done.append("single")
  def local_task_done (self): self.tasks_done.append("local")
  def remote_task_done(self): self.tasks_done.append("remote")
  
  def test_client_or_server__server_side(self):
    set_side("server")
    self.mobile.client_or_server()
    assert self.tasks_done == ["server"]
    
  def test_client_or_server__client_side(self):
    set_side("client")
    self.mobile.client_or_server()
    assert self.tasks_done == ["client"]
    
  def test_client_or_server__single_side(self):
    set_side("single")
    assert not hasattr(self.mobile, "client_or_server")
    
    
  def test_both_client_server__server_side(self):
    set_side("server")
    self.mobile.both_client_server()
    assert self.tasks_done == ["server", "client"]
    
  def test_both_client_server__client_side(self):
    set_side("client")
    self.mobile.both_client_server()
    assert self.tasks_done == ["server", "client"]
    
    
  def test_both_client_server_and_client__server_side(self):
    set_side("server")
    self.mobile.both_client_server_and_client()
    assert self.tasks_done == ["server", "client"]
    
  def test_both_client_server_and_client__client_side(self):
    set_side("client")
    self.mobile.both_client_server_and_client()
    assert self.tasks_done == ["server", "client", "client"]


if __name__ == '__main__': unittest.main()
  
  
