/*
 * ray_intersections.h
 *
 *  Created on: Apr 20, 2018
 *      Author: Maxime Lemonnier
 */
#pragma once

#include "traits.h"
#include <type_traits>
#include <array>

namespace intersections
{
/*
    "An Efficient and Robust Ray-Box Intersection Algorithm"
    Journal of graphics tools, 10(1):49-54, 2005
 *
 */
template <typename Point, size_t Dim = n_coords<Point>::value>
bool intersect_line_box(const Point &origin
        , const Point & inv_direction
        , const std::array<unsigned, Dim> & signs
        , const Point & min
        , const Point & max
        , const scalar_t<Point> & valid_min
        , const scalar_t<Point> & valid_max
        , scalar_t<Point> & p_min
        , scalar_t<Point> & p_max)
{
    typedef scalar_t<Point>  Scalar;
    const Point * parameters[2] = {&min, &max};
    Scalar t_min[Dim], t_max[Dim];

    for(size_t d = 0; d < Dim; d++)
    {
        t_min[d] = ((*parameters[  signs[d]])[d] - origin[d]) * inv_direction[d];
        t_max[d] = ((*parameters[1-signs[d]])[d] - origin[d]) * inv_direction[d];
    }

    p_min = t_min[0];
    p_max = t_max[0];

    for(size_t d = 0; d < Dim-1; d++)
    {
        if ( (p_min > t_max[d+1]) || (t_min[d+1] > p_max) )
            return false;

        if (t_min[d+1] > p_min)
            p_min = t_min[d+1];

        if (t_max[d+1] < p_max)
            p_max = t_max[d+1];
    }
    return ( (p_min < valid_max) && (p_max > valid_min) );
}

template <typename Point, size_t Dim = n_coords<Point>::value>
void signs_and_inv_direction(const Point & direction, std::array<unsigned, Dim> & signs, Point & inv_direction)
{
    for(size_t d = 0; d < Dim; d++)
    {
        inv_direction[d] = 1/direction[d];
        signs[d] = inv_direction[d] < 0 ? 1 : 0;
    }
}
template <typename Point, size_t Dim = n_coords<Point>::value>
decltype(auto) intersect_line_box(const Point &origin
        , const Point & direction
        , const Point & min
        , const Point & max
        , const scalar_t<Point> & valid_min = -std::numeric_limits<scalar_t<Point>>::max()
        , const scalar_t<Point> & valid_max = std::numeric_limits<scalar_t<Point>>::max())
{
    std::array<unsigned, Dim> signs;
    Point inv_direction;
    signs_and_inv_direction(direction, signs, inv_direction);

    scalar_t<Point> p_min, p_max;
    bool r = intersect_line_box<Point, Dim>(origin, inv_direction, signs, min, max, valid_min, valid_max, p_min, p_max);

    return std::make_tuple(r, p_min, p_max);
}

/*
 * Möller-Trumbore ray-triangle interseciton algorithm
 * (implementation inspired from https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/moller-trumbore-ray-triangle-intersection)
 *
 */
template <bool CULLING, typename P1, typename P2>
bool intersect_line_triangle(
    const P1 &origin, const P1 &direction,
    const P2 &v0, const P2 &v1, const P2 &v2,
    P1 &tuv)
{
    typedef scalar_t<P1> Scalar;

    P1 v0v1 = v1 - v0;
    P1 v0v2 = v2 - v0;
    P1 p = direction.cross(v0v2);

    auto det = v0v1.dot(p);

    // if the determinant is negative the triangle is backfacing
    // if the determinant is too close to 0, the ray is too close to be parallel to the triangle
    if ((CULLING ? det : fabs(det)) < std::numeric_limits<Scalar>::epsilon())
        return false;

    auto inv_det = 1 / det;

    P1 t = origin - v0;
    tuv[1] = t.dot(p) * inv_det;
    if (tuv[1] < 0 || tuv[1] > 1)
        return false;

    P1 qvec = t.cross(v0v1);
    tuv[2] = direction.dot(qvec) * inv_det;
    if (tuv[2] < 0 || tuv[1] + tuv[2] > 1)
        return false;

    tuv[0] = v0v2.dot(qvec) * inv_det;
    return true;
}
}
