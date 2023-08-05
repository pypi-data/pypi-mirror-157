/*!
* Different traits helpers
* @author Maxime Lemonnier
*/

#pragma once

#include <type_traits>
#include <Eigen/Dense>

template <typename T>
using remove_const_cv_ref = typename std::remove_const< typename std::remove_reference< typename std::remove_cv< T >::type >::type >::type;

template <typename Point>
using scalar_t = remove_const_cv_ref<decltype(Point()[0])>;

template <typename Point>
struct n_coords;

template <typename T, int R, int C>
struct n_coords< Eigen::Matrix<T, R, C> >
{
        static constexpr size_t value = Eigen::Matrix<T, R, C>::RowsAtCompileTime * Eigen::Matrix<T, R, C>::ColsAtCompileTime;
};
