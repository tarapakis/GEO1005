# -*- coding: utf-8 -*-
"""
/***************************************************************************
 escapers
                                 A QGIS plugin
 where are the animals
                             -------------------
        begin                : 2017-12-15
        copyright            : (C) 2017 by Teng_Takis_Giorgos
        email                : tengwu95@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load escapers class from file escapers.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .escapers import escapers
    return escapers(iface)
