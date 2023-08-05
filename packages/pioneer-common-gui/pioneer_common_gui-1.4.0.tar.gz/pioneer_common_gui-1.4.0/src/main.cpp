/*
 * py_bvh.cpp
 *
 *  Created on: Apr 18, 2018
 *      Author: Maxime Lemonnier
 */

#include <atomic>
#include <thread>
#include <mutex>
#include <algorithm>
#include <functional>
#include <iostream>
#include <numeric>
#include <tbb/parallel_for.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/eigen.h>
#include <pybind11/functional.h>
#include <Eigen/Dense>
#include <unsupported/Eigen/BVH>
#include "BVHWrapper.h"
#include "RayPointsQuery.h"
#include "RayTrianglesQuery.h"

namespace py = pybind11;

using namespace Eigen;
class PyTrianglesBVH
{
public:
    typedef BVHWrapper<int, float,3, 3> Wrapper;
    typedef KdBVH<float, 3, size_t> BVH;
    typedef RayTrianglesQuery<BVH, Wrapper> Query;


    PyTrianglesBVH(const Ref<const Wrapper::Indices> triangles, const Ref<const Wrapper::Points> vertices) :
        _triangles(triangles), _vertices(vertices), _wrapper(_triangles, _vertices)
        , _tree(_wrapper.begin(), _wrapper.end(), _wrapper.boxes_begin(), _wrapper.boxes_end())
    {

    }

    decltype(auto) intersect_ray(const Eigen::Ref<const Query::Point> origin, const Eigen::Ref<const Query::Point> direction, bool keep_closest_only = false)
    {
        Query query(_wrapper, origin, direction);

        BVIntersect(_tree, query);

        auto results = query.sorted();

        auto n_intersections = (keep_closest_only ? 
			std::min(results.size(), size_t(1)) 
			: results.size());

        Matrix<int, Dynamic, 1u> ids;
        Matrix<float, Dynamic, 3u> tuvs;

        ids.resize(n_intersections, 1);
        tuvs.resize(n_intersections, 3);

        for(size_t i = 0; i < n_intersections; i++)
        {
                ids[i] = results[i].id;
                tuvs.row(i) = results[i].tuv;
        }
        return std::make_tuple(ids, tuvs);
    }

    decltype(auto) intersect_rays(const Ref<const Wrapper::Points> origins, const Ref<const Wrapper::Points> directions, float threshold = 0.f, bool keep_closest_only = false)
    {
        size_t n_rays = origins.rows();

        std::vector<Query::Intersections> results(n_rays);
        tbb::parallel_for(size_t(0), n_rays, [&](auto i)
        //for(size_t i = 0; i < n_rays; i++)
        {
            Query query(_wrapper, origins.row(i), directions.row(i));
            BVIntersect(_tree, query);

            if(threshold > 0 && query.intersections.empty())
            {
                if(BVMinimize(_tree, query) < threshold)
                    results[i].emplace_back(Query::Intersection{query.minimum.id, query.minimum.tuv});
            }
            else
                results[i] = std::move(query.sorted());

        }
        );

        Matrix<int, Dynamic, 1u> offsets;
        Matrix<int, Dynamic, 1u> ids;
        Matrix<float, Dynamic, 3u> tuvs;
	
		using namespace std;
		
        size_t n_intersections = std::accumulate(results.begin()
		, results.end()
		, size_t(0u)
		, [&](const size_t & s, const Query::Intersections & result)
		{
			return s + (keep_closest_only ? 
			min(result.size(), size_t(1)) 
			: result.size());
		});

        offsets.resize(n_rays+1, 1);
        ids.resize(n_intersections, 1);
        tuvs.resize(n_intersections, 3);

        size_t ray_i = 0;
        size_t i = 0;
        offsets[0] = 0;
        std::for_each(results.begin(), results.end(), [&](const Query::Intersections & result)
        {
            for(size_t r = 0; r < result.size(); r++)
            {

                ids[i] = result[r].id;
                tuvs.row(i) = result[r].tuv;
                i++;
                if(keep_closest_only)
                    break;
            }
            offsets[++ray_i] = i;
        });
        return std::make_tuple(offsets, ids, tuvs);
    }


    decltype(auto) ray_distance(const Eigen::Ref<const Query::Point> origin, const Eigen::Ref<const Query::Point> direction)
    {
        Query query(_wrapper, origin, direction);

        BVMinimize(_tree, query);

        return std::make_tuple(query.minimum.id, query.minimum.distance, query.minimum.tuv);
    }

    decltype(auto) rays_distances(const Ref<const Wrapper::Points> origins, const Ref<const Wrapper::Points> directions)
    {
        size_t n_rays = origins.rows();
        Matrix<int, Dynamic, 1u> ids;
        Matrix<float, Dynamic, 1u> distances;
        Matrix<float, Dynamic, 3u> tuvs;

        ids.resize(n_rays, 1);
        distances.resize(n_rays, 1);
        tuvs.resize(n_rays, 3);
        tbb::parallel_for(size_t(0), n_rays, [&](auto i)
        //for(size_t i = 0; i < n_rays; i++)
        {
            Query query(_wrapper, origins.row(i), directions.row(i));
            BVMinimize(_tree, query);
            ids[i] = query.minimum.id;
            distances[i] = query.minimum.distance;
            tuvs.row(i) = query.minimum.tuv;
        }
        );

        return std::make_tuple(ids, distances, tuvs);
    }
    const Wrapper::Indices _triangles; //TODO avoid copy
    const Wrapper::Points _vertices;
    Wrapper _wrapper;
    BVH _tree;
};


class PyPointsBVH
{
public:
    typedef BVHWrapper<int, float, 1, 3> Wrapper;
    typedef KdBVH<float, 3, size_t> BVH;
    typedef RayPointsQuery<BVH, Wrapper> Query;


    PyPointsBVH(const Ref<const Wrapper::Indices> indices, const Ref<const Wrapper::Points> vertices) :
        _indices(indices), _vertices(vertices), _wrapper(_indices, _vertices)
        , _tree(_wrapper.begin(), _wrapper.end(), _wrapper.boxes_begin(), _wrapper.boxes_end())
    {
    }

    decltype(auto) ray_distance(const Eigen::Ref<const Query::Point> origin, const Eigen::Ref<const Query::Point> direction)
    {
        Query query(_wrapper, origin, direction);

        BVMinimize(_tree, query);

        return std::make_tuple(query.minimum.id, query.minimum.distance, query.minimum.t);
    }

    decltype(auto) rays_distances(const Ref<const Wrapper::Points> origins, const Ref<const Wrapper::Points> directions)
    {
        size_t n_rays = origins.rows();
        Matrix<int, Dynamic, 1u> ids;
        Matrix<float, Dynamic, 1u> distances;
        Matrix<float, Dynamic, 1u> t;

        ids.resize(n_rays, 1);
        distances.resize(n_rays, 1);
        t.resize(n_rays, 3);
        tbb::parallel_for(size_t(0), n_rays, [&](auto i)
        //for(size_t i = 0; i < n_rays; i++)
        {
            Query query(_wrapper, origins.row(i), directions.row(i));
            BVMinimize(_tree, query);
            ids[i] = query.minimum.id;
            distances[i] = query.minimum.distance;
            t[i] = query.minimum.t;
        }
        );

        return std::make_tuple(ids, distances, t);
    }
    const Wrapper::Indices _indices; //TODO avoid copy
    const Wrapper::Points _vertices;
    Wrapper _wrapper;
    BVH _tree;
};

PYBIND11_MODULE(leddar_utils_cpp, m) {
    py::class_<PyTrianglesBVH>(m, "BVH")
        .def(py::init<const Ref<const PyTrianglesBVH::Wrapper::Indices>, const Ref<const PyTrianglesBVH::Wrapper::Points>>())
        .def("intersect_ray", &PyTrianglesBVH::intersect_ray)
        .def("intersect_rays", &PyTrianglesBVH::intersect_rays)
        .def("ray_distance", &PyTrianglesBVH::ray_distance)
        .def("rays_distances", &PyTrianglesBVH::rays_distances)
        .def_readonly("triangles", &PyTrianglesBVH::_triangles)
        .def_readonly("vertices", &PyTrianglesBVH::_vertices)
        ;

    py::class_<PyPointsBVH>(m, "PointsBVH")
        .def(py::init<const Ref<const PyPointsBVH::Wrapper::Indices>, const Ref<const PyPointsBVH::Wrapper::Points> >())
        .def("ray_distance", &PyPointsBVH::ray_distance)
        .def("rays_distances", &PyPointsBVH::rays_distances)
        .def_readonly("vertices", &PyPointsBVH::_vertices)
        ;

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
