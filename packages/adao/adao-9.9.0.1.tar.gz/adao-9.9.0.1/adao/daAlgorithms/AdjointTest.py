# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2022 EDF R&D
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#
# Author: Jean-Philippe Argaud, jean-philippe.argaud@edf.fr, EDF R&D

import numpy
from daCore import BasicObjects, NumericObjects, PlatformInfo
mpr = PlatformInfo.PlatformInfo().MachinePrecision()

# ==============================================================================
class ElementaryAlgorithm(BasicObjects.Algorithm):
    def __init__(self):
        BasicObjects.Algorithm.__init__(self, "ADJOINTTEST")
        self.defineRequiredParameter(
            name     = "ResiduFormula",
            default  = "ScalarProduct",
            typecast = str,
            message  = "Formule de résidu utilisée",
            listval  = ["ScalarProduct"],
            )
        self.defineRequiredParameter(
            name     = "EpsilonMinimumExponent",
            default  = -8,
            typecast = int,
            message  = "Exposant minimal en puissance de 10 pour le multiplicateur d'incrément",
            minval   = -20,
            maxval   = 0,
            )
        self.defineRequiredParameter(
            name     = "InitialDirection",
            default  = [],
            typecast = list,
            message  = "Direction initiale de la dérivée directionnelle autour du point nominal",
            )
        self.defineRequiredParameter(
            name     = "AmplitudeOfInitialDirection",
            default  = 1.,
            typecast = float,
            message  = "Amplitude de la direction initiale de la dérivée directionnelle autour du point nominal",
            )
        self.defineRequiredParameter(
            name     = "SetSeed",
            typecast = numpy.random.seed,
            message  = "Graine fixée pour le générateur aléatoire",
            )
        self.defineRequiredParameter(
            name     = "ResultTitle",
            default  = "",
            typecast = str,
            message  = "Titre du tableau et de la figure",
            )
        self.defineRequiredParameter(
            name     = "StoreSupplementaryCalculations",
            default  = [],
            typecast = tuple,
            message  = "Liste de calculs supplémentaires à stocker et/ou effectuer",
            listval  = [
                "CurrentState",
                "Residu",
                "SimulatedObservationAtCurrentState",
                ]
            )
        self.requireInputArguments(
            mandatory= ("Xb", "HO" ),
            optional = ("Y", ),
            )
        self.setAttributes(tags=(
            "Checking",
            ))

    def run(self, Xb=None, Y=None, U=None, HO=None, EM=None, CM=None, R=None, B=None, Q=None, Parameters=None):
        self._pre_run(Parameters, Xb, Y, U, HO, EM, CM, R, B, Q)
        #
        Hm = HO["Direct"].appliedTo
        Ht = HO["Tangent"].appliedInXTo
        Ha = HO["Adjoint"].appliedInXTo
        #
        Perturbations = [ 10**i for i in range(self._parameters["EpsilonMinimumExponent"],1) ]
        Perturbations.reverse()
        #
        Xn       = numpy.ravel( Xb ).reshape((-1,1))
        NormeX  = numpy.linalg.norm( Xn )
        if Y is None:
            Yn = numpy.ravel( Hm( Xn ) ).reshape((-1,1))
        else:
            Yn = numpy.ravel( Y ).reshape((-1,1))
        NormeY = numpy.linalg.norm( Yn )
        if self._toStore("CurrentState"):
            self.StoredVariables["CurrentState"].store( Xn )
        if self._toStore("SimulatedObservationAtCurrentState"):
            self.StoredVariables["SimulatedObservationAtCurrentState"].store( Yn )
        #
        dX0 = NumericObjects.SetInitialDirection(
            self._parameters["InitialDirection"],
            self._parameters["AmplitudeOfInitialDirection"],
            Xn,
            )
        #
        # Entete des resultats
        # --------------------
        __marge =  12*u" "
        __precision = u"""
            Remarque : les nombres inferieurs a %.0e (environ) representent un zero
                       a la precision machine.\n"""%mpr
        if self._parameters["ResiduFormula"] == "ScalarProduct":
            __entete = u"  i   Alpha     ||X||       ||Y||       ||dX||        R(Alpha)"
            __msgdoc = u"""
            On observe le residu qui est la difference de deux produits scalaires :

              R(Alpha) = | < TangentF_X(dX) , Y > - < dX , AdjointF_X(Y) > |

            qui doit rester constamment egal a zero a la precision du calcul.
            On prend dX0 = Normal(0,X) et dX = Alpha*dX0. F est le code de calcul.
            Y doit etre dans l'image de F. S'il n'est pas donne, on prend Y = F(X).\n""" + __precision
        #
        if len(self._parameters["ResultTitle"]) > 0:
            __rt = str(self._parameters["ResultTitle"])
            msgs  = u"\n"
            msgs += __marge + "====" + "="*len(__rt) + "====\n"
            msgs += __marge + "    " + __rt + "\n"
            msgs += __marge + "====" + "="*len(__rt) + "====\n"
        else:
            msgs  = u""
        msgs += __msgdoc
        #
        __nbtirets = len(__entete) + 2
        msgs += "\n" + __marge + "-"*__nbtirets
        msgs += "\n" + __marge + __entete
        msgs += "\n" + __marge + "-"*__nbtirets
        #
        # ----------
        for i,amplitude in enumerate(Perturbations):
            dX          = amplitude * dX0
            NormedX     = numpy.linalg.norm( dX )
            #
            TangentFXdX = numpy.ravel( Ht( (Xn,dX) ) )
            AdjointFXY  = numpy.ravel( Ha( (Xn,Yn)  ) )
            #
            Residu = abs(float(numpy.dot( TangentFXdX, Yn ) - numpy.dot( dX, AdjointFXY )))
            #
            msg = "  %2i  %5.0e   %9.3e   %9.3e   %9.3e   |  %9.3e"%(i,amplitude,NormeX,NormeY,NormedX,Residu)
            msgs += "\n" + __marge + msg
            #
            self.StoredVariables["Residu"].store( Residu )
        #
        msgs += "\n" + __marge + "-"*__nbtirets
        msgs += "\n"
        #
        # Sorties eventuelles
        # -------------------
        print("\nResults of adjoint check by \"%s\" formula:"%self._parameters["ResiduFormula"])
        print(msgs)
        #
        self._post_run(HO)
        return 0

# ==============================================================================
if __name__ == "__main__":
    print('\n AUTODIAGNOSTIC\n')
