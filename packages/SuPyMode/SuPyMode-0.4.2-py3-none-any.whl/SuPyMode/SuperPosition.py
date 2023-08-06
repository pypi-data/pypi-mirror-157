import numpy as np

from SuPyMode.Tools.BaseClass import ReprBase

class SuperPosition(ReprBase):
    Description = 'Mode superposition class'
    ReprVar     = ["Amplitudes"]

    def __init__(self, SuperSet, InitialAmplitudes: list):
        self.SuperSet   = SuperSet
        self.InitialAmplitudes = np.asarray(InitialAmplitudes).astype(complex)
        self._CouplerLength    = None
        self._Amplitudes       = None
        self.Init()



    def Init(self):
        shape = [len(self.InitialAmplitudes)] + list(self.SuperSet[0].FullFields.shape)

        self.Fields = np.zeros(shape)
        for n, mode in enumerate(self.SuperSet.SuperModes):
            self.Fields[n] = mode.FullFields


    def ComputeAmpltiudes(self, TotalLength: float, rTol: float = 1e-8, aTol: float = 1e-7, MaxStep: float = np.inf):
        self.MatrixInterp = interp1d(self.Distance, self.SuperSet.Matrix, axis=-1)

        def foo(t, y):
            return 1j * self.MatrixInterp(t).dot(y)

        sol = solve_ivp(foo,
                        y0       = self.InitialAmplitudes,
                        t_span   = [0, self._CouplerLength],
                        method   = 'RK45',
                        rtol     = rTol,
                        atol     = aTol,
                        max_step = MaxStep)

        self.Amplitudes = sol.y
        self.Distances  = sol.t
        self.AmplitudeInterpolation = interp1d(self.Distances, self.Amplitudes, axis=-1)


    @property
    def ITRList(self):
        return self.SuperSet.ITRList


    @property
    def CouplerLength(self):
        assert self._CouplerLength is not None, "CouplerLength attribute has to be defined before computing propagation."
        return self._CouplerLength


    @CouplerLength.setter
    def CouplerLength(self, Value: float):
        self._CouplerLength = Value
        self.Distance = np.linspace(0, self._CouplerLength, self.ITRList.size)


    @property
    def Amplitudes(self):
        if self._Amplitudes is None:
            self.ComputeAmpltiudes()

        return self._Amplitudes


    @Amplitudes.setter
    def Amplitudes(self, Value):
        self._Amplitudes = Value


    def PlotAmplitudes(self):
        Fig = Scene('SuPyMode Figure', UnitSize=(10,4))

        A = self.InitialAmplitudes.dot(self.Amplitudes)
        z = self.Distances

        Fig.AddLine(Row      = 0,
                      Col      = 0,
                      x        = z,
                      y        = A.real,
                      Fill     = False,
                      Legend   = r"$\Re${A}",
                      xLabel   = r'Z-Distance [$\mu m$]',
                      yLabel   = r'Mode complex ampltiude [normalized]')

        scene.AddLine(Row      = 0,
                      Col      = 0,
                      x        = z,
                      y        = np.abs(A),
                      Fill     = False,
                      Legend   = r"|A|",
                      xLabel   = r'Z-Distance [$\mu m$]',
                      yLabel   = r'Mode complex ampltiude [normalized]')


        scene.SetAxes(0, 0, Equal=False, Legend=True)
        scene.Show()


    def PlotField(self, Slices: list=[0]):
        Fig = Scene('SuPyMode Figure', UnitSize=(4,4))

        Colorbar = ColorBar(Discreet=False, Position='bottom')
        for n, slice in enumerate(Slices):

            ax = Axis(Row              = 0,
                      Col              = n,
                      xLabel           = r'x [$\mu m$]',
                      yLabel           = r'y [$\mu m$]',
                      Title            = f'Mode field  [ITR: {self.ITRList[slice]:.2f}]',
                      Legend           = False,
                      Grid             = False,
                      Equal            = True,
                      Colorbar         = Colorbar,
                      xScale           = 'linear',
                      yScale           = 'linear')


            artist = Mesh(X           = self.SuperSet.FullxAxis,
                          Y           = self.SuperSet.FullyAxis,
                          Scalar      = self.Fields[0,slice,...],
                          ColorMap    = FieldMap,
                          )

            ax.AddArtist(artist)

            Fig.AddAxes(ax)

        Fig.Show()



    def PlotPropagation(self):
        if self._Amplitudes is None: self.ComputeAmpltiudes()

        y = self.AmplitudeInterpolation(self.Distance)

        z = self.Distance

        Field = self.SuperSet[0].FullFields.astype(complex)*0.

        for mode, _ in enumerate(self.InitialAmplitudes):
            a = y[mode].astype(complex)
            field = self.SuperSet[mode].FullFields.astype(complex)
            Field += np.einsum('i, ijk->ijk', a, field)

        surface = mlab.surf( np.abs( Field[0] ) , warp_scale="auto" )

        @mlab.animate(delay=100)
        def anim_loc():
            for n, _ in enumerate(self.Distance):
                surface.mlab_source.scalars = np.abs(np.abs( Field[n] ) )

                yield

        anim_loc()
        mlab.show()
