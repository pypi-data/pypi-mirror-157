# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from abc import abstractmethod

from ..base import Base


class ComponentBase(Base):

    @abstractmethod
    def sync(self):
        raise NotImplementedError("The class does not have a sync method.")
