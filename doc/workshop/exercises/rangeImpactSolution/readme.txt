GOAL
 - Calculate Range (R) and Impact (I)
    - Mean, Sigma, Minimum, Maximum
 - Sensitivity of I, R
    - with respect to v, theta, g

#####################################
Models:

rangefinder.py
 - inputs:
    - v0, 20 to 40 m/s
    - th0, 10 to 70 degrees
    - g, 9.7639 to 9.8337 m/s/s
 - outputs: vf, R

impact.py
 - inputs:
    - m, constant 1 kg (see manual!)
    - vf, from rangefinder
 - outputs: I

#####################################
To Be Done:
<Steps>
<ExternalModel> for rangefinder, impact
<EnsembleModel>
<Samplers>
<Distributions>


#####################################
BONUSES

  - Create a ROM of the EnsembleModel
     and compare to the original!

  - Add an input for "impact time"
     to perturb in "impact.py"

#####################################
Check Out Exercise:
 - git checkout workshop
 - git pull
 raven/doc/workshop/exercises
