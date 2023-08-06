#include <pln/core/image_cast.hpp>

#include <pybind11/pybind11.h>

#include "morpho/morpho.hpp"

namespace pln
{
  PYBIND11_MODULE(pylena_cxx, m)
  {
    pln::init_pylena_numpy(m);
    pln::morpho::define_morpho(m);
  }
} // namespace pln