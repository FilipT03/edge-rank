#include <pybind11/pybind11.h>
#include "calculations.cpp"

PYBIND11_MODULE(cpp_module, m) {
    m.doc() = "Cpp module for faster calculations";
//    m.def("load_simple_cpp", &LoadSimple, "Loads simple formats");
    m.def("generate_affinity_graph", &GenerateAffinityGraph, "Generates affinity graph");
    m.def("generate_popularity_map", &GeneratePopularityMap, "Generates popularity map");
}
