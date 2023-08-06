#pragma once

class EigenSolving : public BaseLaplacian
{
  public:
    size_t             nMode, sMode, MaxIter, DegenerateFactor, ITRLength, Order, ExtrapolOrder;
    ScalarType         Tolerance, k, kInit, kDual, lambda, MaxIndex;
    ScalarType        *MeshPtr, *ITRPtr;
    std::vector<double> ITRList;
    MSparse            EigenMatrix, Identity, M;
    VectorType         MeshGradient;
    BiCGSTAB<MSparse>  Solver;
    std::vector<SuperMode> SuperModes, SortedSuperModes;

  EigenSolving(ndarray&   Mesh,
               ndarray&   PyMeshGradient,
               size_t     nMode,
               size_t     sMode,
               size_t     MaxIter,
               ScalarType Tolerance,
               ScalarType dx,
               ScalarType dy,
               ScalarType Wavelength,
               bool       Debug)
               : BaseLaplacian(Mesh, dx, dy)
                {
                 this->Debug             = Debug;
                 this->nMode             = nMode;
                 this->sMode             = sMode;
                 this->MaxIter           = MaxIter;
                 this->Tolerance         = Tolerance;

                 this->MeshPtr           = (ScalarType*) Mesh.request().ptr;
                 this->lambda            = Wavelength;
                 this->k                 = 2.0 * PI / Wavelength;
                 this->kInit             = this->k;
                 ScalarType *adress      = (ScalarType*) PyMeshGradient.request().ptr;

                 Map<VectorType> MeshGradient( adress, size );
                 this->MeshGradient = MeshGradient;

                 for (int i=0; i<nMode; ++i)
                    SuperModes.push_back(SuperMode(i));

                 for (int i=0; i<sMode; ++i)
                    SortedSuperModes.push_back(SuperMode(i));

                 ComputeMaxIndex();


               }



   void      PopulateModes(size_t Slice, MatrixType& EigenVectors, VectorType& EigenValues);
   SuperMode GetMode(size_t Mode){ return SortedSuperModes[Mode]; }

   void      PrepareSuperModes();
   void      SwapMode(SuperMode &Mode0, SuperMode &Mode1);
   void      SortSliceIndex(size_t Slice);
   void      SortSliceFields(size_t Slice);

   void      LoopOverITR(std::vector<double> ITRList, size_t order);

   tuple<ndarray, ndarray> GetSlice(size_t slice);


   tuple<MatrixType, VectorType> ComputeEigen(ScalarType alpha);

   ScalarType                    ComputeMaxIndex();

   MSparse                       ComputeMatrix();

   void                          ComputeCoupling();
   void                          ComputeAdiabatic();
   vector<size_t>                ComputecOverlaps(size_t idx);
   void                          ComputeLaplacian(size_t order);
   void                          ComputeCouplingAdiabatic();

   void SortModesFields();
   void SortModesIndex();
   void SortModes(std::string Type);
   void SortModesNone();

};
