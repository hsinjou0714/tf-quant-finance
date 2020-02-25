# Lint as: python3
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Calculation of the Black-Scholes implied volatility via Newton's method."""

import enum

from tf_quant_finance.black_scholes import implied_vol_approximation as approx
from tf_quant_finance.black_scholes import implied_vol_newton_root as newton


@enum.unique
class ImpliedVolMethod(enum.Enum):
  FAST_APPROX = 1  # A faster but approximate method.
  NEWTON = 2  # Uses Newton root search to find an accurate value.


def implied_vol(*,
                prices,
                strikes,
                expiries,
                spots=None,
                forwards=None,
                discount_factors=None,
                is_call_options=None,
                method=ImpliedVolMethod.NEWTON,
                validate_args=False,
                dtype=None,
                name=None,
                **kwargs):
  """Finds the implied volatilities of options under the Black Scholes model.

  #### Examples
  ```python
  forwards = np.array([1.0, 1.0, 1.0, 1.0])
  strikes = np.array([1.0, 2.0, 1.0, 0.5])
  expiries = np.array([1.0, 1.0, 1.0, 1.0])
  discount_factors = np.array([1.0, 1.0, 1.0, 1.0])
  option_signs = np.array([1.0, 1.0, -1.0, -1.0])
  volatilities = np.array([1.0, 1.0, 1.0, 1.0])
  prices = black_scholes.option_price(
      forwards,
      strikes,
      volatilities,
      expiries,
      discount_factors=discount_factors,
      is_call_options=is_call_options)
  implied_vols = newton_vol.implied_vol(forwards,
                                        strikes,
                                        expiries,
                                        discount_factors,
                                        prices,
                                        option_signs)
  with tf.Session() as session:
    print(session.run(implied_vols[0]))
  # Expected output:
  # [ 1.  1.  1.  1.]

  Args:
    prices: A real `Tensor` of any shape. The prices of the options whose
      implied vol is to be calculated.
    strikes: A real `Tensor` of the same dtype as `prices` and a shape that
      broadcasts with `prices`. The strikes of the options.
    expiries: A real `Tensor` of the same dtype as `prices` and a shape that
      broadcasts with `prices`. The expiry for each option. The units should be
      such that `expiry * volatility**2` is dimensionless.
    spots: A real `Tensor` of any shape that broadcasts to the shape of the
      `prices`. The current spot price of the underlying. Either this argument
      or the `forwards` (but not both) must be supplied.
    forwards: A real `Tensor` of any shape that broadcasts to the shape of
      `prices`. The forwards to maturity. Either this argument or the `spots`
      must be supplied but both must not be supplied.
    discount_factors: An optional real `Tensor` of same dtype as the `prices`.
      If not None, these are the discount factors to expiry (i.e. e^(-rT)). If
      None, no discounting is applied (i.e. it is assumed that the undiscounted
      option prices are provided ). If `spots` is supplied and
      `discount_factors` is not None then this is also used to compute the
      forwards to expiry.
      Default value: None, equivalent to discount factors = 1.
    is_call_options: A boolean `Tensor` of a shape compatible with `prices`.
      Indicates whether the option is a call (if True) or a put (if False). If
      not supplied, call options are assumed.
    method: Enum value of ImpliedVolMethod to select the algorithm to use to
      infer the implied volatility.
    validate_args: A Python bool. If True, indicates that arguments should be
      checked for correctness before performing the computation. The checks
      performed are: (1) Forwards and strikes are positive. (2) The prices
        satisfy the arbitrage bounds (i.e. for call options, checks the
        inequality `max(F-K, 0) <= Price <= F` and for put options, checks that
        `max(K-F, 0) <= Price <= K`.). (3) Checks that the prices are not too
        close to the bounds. It is numerically unstable to compute the implied
        vols from options too far in the money or out of the money.
    dtype: `tf.Dtype` to use when converting arguments to `Tensor`s. If not
      supplied, the default TensorFlow conversion will take place. Note that
      this argument does not do any casting for `Tensor`s or numpy arrays.
      Default value: None.
    name: (Optional) Python str. The name prefixed to the ops created by this
      function. If not supplied, the default name 'implied_vol' is used.
      Default value: None
    **kwargs: Any other keyword arguments to be passed to the specific
      implementation. (See black_scholes.implied_vol_approx and
      black_scholes.implied_vol_newton for details).

  Returns:
    implied_vols: A `Tensor` of the same dtype as `prices` and shape as the
      common broadcasted shape of `(prices, spots/forwards, strikes, expiries)`.
      The implied volatilities as inferred by the chosen method.

  Raises:
    ValueError: If both `forwards` and `spots` are supplied or if neither is
      supplied.
  """
  if method == ImpliedVolMethod.FAST_APPROX:
    return approx.implied_vol(
        prices=prices,
        strikes=strikes,
        expiries=expiries,
        spots=spots,
        forwards=forwards,
        discount_factors=discount_factors,
        is_call_options=is_call_options,
        validate_args=validate_args,
        dtype=dtype,
        name=name,
        **kwargs)
  if method == ImpliedVolMethod.NEWTON:
    return newton.implied_vol(
        prices=prices,
        strikes=strikes,
        expiries=expiries,
        spots=spots,
        forwards=forwards,
        discount_factors=discount_factors,
        is_call_options=is_call_options,
        validate_args=validate_args,
        dtype=dtype,
        name=name,
        **kwargs)[0]
  raise ValueError('Unknown implied vol method {}'.format(method))
