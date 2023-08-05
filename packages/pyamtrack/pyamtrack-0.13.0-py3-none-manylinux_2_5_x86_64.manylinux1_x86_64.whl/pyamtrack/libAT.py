import warnings
from .lib import _libAT
from cffi import FFI
ffi = _libAT.ffi

from enum import Enum

AT_ERModels = Enum('AT_ERModels', ffi.typeof('enum AT_ERModels').relements)
AT_RBEModels = Enum('AT_RBEModels', ffi.typeof('enum AT_RBEModels').relements)
material_no = Enum('material_no', ffi.typeof('enum material_no').relements)
material_phase = Enum('material_phase', ffi.typeof('enum material_phase').relements)
AT_GammaResponseModels = Enum('AT_GammaResponseModels', ffi.typeof('enum AT_GammaResponseModels').relements)
stoppingPowerSource_no = Enum('stoppingPowerSource_no', ffi.typeof('enum stoppingPowerSource_no').relements)
RDDModels = Enum('RDDModels', ffi.typeof('enum RDDModels').relements)
TRPSPCBTAG_FILETYPE=1
TRPSPCBTAG_FILEVERSION=2
TRPSPCBTAG_FILEDATE=3
TRPSPCBTAG_TARGNAME=4
TRPSPCBTAG_PROJNAME=5
TRPSPCBTAG_B=6
TRPSPCBTAG_P=7
TRPSPCBTAG_N=8
TRPSPCBTAG_NZ=9
TRPSPCDTAG_Z=10
TRPSPCDTAG_N=11
TRPSPCDTAG_NS=12
TRPSPCDTAG_S=13
TRPSPCDTAG_CUM=14
TRPSPCDTAG_NC=15
TRPSPCDTAG_NE=16
TRPSPCDTAG_E=17
TRPSPCDTAG_EREF=18
TRPSPCDTAG_HISTO=19
TRPSPCDTAG_RUNNINGSUM=20
def getERName(p_ER_no, p_ER_name):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns name of the electron model from index
	@param[in]   ER_no    electron-range-model index
	@param[out]  ER_name  string containing the electron-range model name
	@return      Status code
	"""
	if not isinstance(p_ER_name, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_ER_name) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_ER_name.clear()
		p_ER_name += ['']
	
	p_ER_no__internal = p_ER_no
	arg_keepalive = [ffi.new("char[]", 1)]
	p_ER_name__internal = ffi.new("char* []", arg_keepalive)
	ret = _libAT.lib.getERName(p_ER_no__internal.encode() if type(p_ER_no__internal) is str else p_ER_no__internal
			,p_ER_name__internal[0].encode() if type(p_ER_name__internal[0]) is str else p_ER_name__internal[0]
			)
	for i,v in enumerate(p_ER_name__internal):
		p_ER_name[i] = ffi.string(v).decode()
	
	return ret
	

def AT_ER_ButtsKatz_range_g_cm2(p_wmax_keV):
	"""
	Wrapping function generated for C language function documented as follows:
	1e-5 * wmax_keV
	@param[in] wmax_keV
	@return
	"""
	p_wmax_keV__internal = p_wmax_keV
	ret = _libAT.lib.AT_ER_ButtsKatz_range_g_cm2(p_wmax_keV__internal.encode() if type(p_wmax_keV__internal) is str else p_wmax_keV__internal
			)
	return ret
	

def AT_ER_Waligorski_range_g_cm2(p_wmax_keV):
	"""
	Wrapping function generated for C language function documented as follows:
	6e-6 * pow( wmax_keV, alpha )
	@param[in] wmax_keV
	@return
	"""
	p_wmax_keV__internal = p_wmax_keV
	ret = _libAT.lib.AT_ER_Waligorski_range_g_cm2(p_wmax_keV__internal.encode() if type(p_wmax_keV__internal) is str else p_wmax_keV__internal
			)
	return ret
	

def AT_ER_Edmund_range_g_cm2(p_wmax_keV):
	"""
	Wrapping function generated for C language function documented as follows:
	6.13*1e-6  * pow( wmax_keV, alpha )
	@param[in] wmax_keV
	@return
	"""
	p_wmax_keV__internal = p_wmax_keV
	ret = _libAT.lib.AT_ER_Edmund_range_g_cm2(p_wmax_keV__internal.encode() if type(p_wmax_keV__internal) is str else p_wmax_keV__internal
			)
	return ret
	

def AT_ER_Geiss_range_g_cm2(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	4e-5 * pow(E_MeV_u, 1.5)
	@param[in] E_MeV_u
	@return
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_ER_Geiss_range_g_cm2(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_ER_Scholz_range_g_cm2(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	5e-5 * pow(E_MeV_u, 1.7)
	@param[in] E_MeV_u
	@return
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_ER_Scholz_range_g_cm2(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_ER_Tabata_range_g_cm2(p_beta, p_a1_g_cm2, p_a2, p_a3, p_a4, p_a5):
	"""
	Wrapping function generated for C language function documented as follows:
	tau = T / mc2 = 2 * beta^2 / (1 - beta^2)
	Rex = a1*(((log(1 + a2 * tau))/a2) - ((a3*tau)/(1 + a4*tau^a5)) )
	Implementation of equation (6) from 10.1016/0029-554x(72)90463-6
	@param[in] beta
	@param[in] a1_g_cm2
	@param[in] a2
	@param[in] a3
	@param[in] a4
	@param[in] a5
	@return range
	"""
	p_beta__internal = p_beta
	p_a1_g_cm2__internal = p_a1_g_cm2
	p_a2__internal = p_a2
	p_a3__internal = p_a3
	p_a4__internal = p_a4
	p_a5__internal = p_a5
	ret = _libAT.lib.AT_ER_Tabata_range_g_cm2(p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			,p_a1_g_cm2__internal.encode() if type(p_a1_g_cm2__internal) is str else p_a1_g_cm2__internal
			,p_a2__internal.encode() if type(p_a2__internal) is str else p_a2__internal
			,p_a3__internal.encode() if type(p_a3__internal) is str else p_a3__internal
			,p_a4__internal.encode() if type(p_a4__internal) is str else p_a4__internal
			,p_a5__internal.encode() if type(p_a5__internal) is str else p_a5__internal
			)
	return ret
	

def AT_ER_Scholz_new_range_g_cm2(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	6.2e-5 * pow(E_MeV_u, 1.7)
	@param[in] E_MeV_u
	@return
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_ER_Scholz_new_range_g_cm2(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_ER_Kiefer_range_g_cm2(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	6.16e-5 * pow(E_MeV_u, 1.7)
	@param[in] E_MeV_u
	@return
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_ER_Kiefer_range_g_cm2(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_max_electron_ranges_m(p_E_MeV_u, p_material_no, p_er_model, p_max_electron_range_m):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the maximum electron range (track radius) in m
	for a given parametrization
	@param[in]  number_of_particles          number of particles in the incident field
	@param[in]  E_MeV_u                      kinetic energy for particles in the given field (array of size number_of_particles)
	@param[in]  material_no                  material index
	@param[in]  er_model                     electron-range model index
	@param[out] max_electron_range_m         electron range (track radius) in m  (array of size number_of_particles)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_max_electron_range_m is passed correctly:
	if len(p_max_electron_range_m) != len(p_E_MeV_u):
		out_array_auto_init = "\nWarning: OUT array parameter p_max_electron_range_m was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_max_electron_range_m.clear()
		p_max_electron_range_m += [0]*len(p_E_MeV_u)
	
	# Array sizes variables initialization:
	p_number_of_particles = len(p_E_MeV_u)
	p_number_of_particles__internal = p_number_of_particles
	p_E_MeV_u__internal = p_E_MeV_u
	p_material_no__internal = p_material_no
	p_er_model__internal = p_er_model
	p_max_electron_range_m__internal = ffi.new("double[]", p_number_of_particles)
	for i,v in enumerate(p_max_electron_range_m):
		p_max_electron_range_m__internal[i] = v
	
	_libAT.lib.AT_max_electron_ranges_m(p_number_of_particles__internal.encode() if type(p_number_of_particles__internal) is str else p_number_of_particles__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_max_electron_range_m__internal.encode() if type(p_max_electron_range_m__internal) is str else p_max_electron_range_m__internal
			)
	for i,v in enumerate(p_max_electron_range_m__internal):
		p_max_electron_range_m[i] = v
	
	

def AT_max_electron_range_m(p_E_MeV_u, p_material_no, p_er_model):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the maximum electron range (track diameter) in m for given energy
	@param[in]  E_MeV_u                      kinetic energy for particles in the given field
	@param[in]  material_no                  index for detector material
	@param[in]  er_model                     index for electron-range model chosen
	@return                                  electron range (track diameter) in m
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_material_no__internal = p_material_no
	p_er_model__internal = p_er_model
	ret = _libAT.lib.AT_max_electron_range_m(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			)
	return ret
	

def AT_max_location_Bortfeld_cm(p_E_MeV, p_sigma_E_MeV, p_material_no, p_eps):
	"""
	Wrapping function generated for C language function documented as follows:
	@brief Proton analytical models of dose, LET and RBE
	Location of maximum dose according to Bortfeld dose model
	@see AT_dose_Bortfeld_Gy_single
	@param[in] E_MeV           initial kinetic energy of proton beam [MeV/u]
	@param[in] sigma_E_MeV     kinetic energy spread (standard deviation) [MeV/u]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in] material_no     material code number
	@see          AT_DataMaterial.h for definition
	@param[in] eps             fraction of primary fluence contributing to the tail of energy spectrum
	if negative a default value of 0.03 is assumed
	@return                    depth at which dose reaches maximum value [cm]
	"""
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_material_no__internal = p_material_no
	p_eps__internal = p_eps
	ret = _libAT.lib.AT_max_location_Bortfeld_cm(p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_eps__internal.encode() if type(p_eps__internal) is str else p_eps__internal
			)
	return ret
	

def AT_range_Bortfeld_cm(p_E_MeV, p_sigma_E_MeV, p_material_no, p_eps, p_dose_drop, p_search_direction):
	"""
	Wrapping function generated for C language function documented as follows:
	Range defined as the location on distal part where dose drops to certain fraction of maximum value.
	@see AT_dose_Bortfeld_Gy_single for details of Bortfeld dose models
	@param[in] E_MeV           initial kinetic energy of proton beam [MeV/u]
	@param[in] sigma_E_MeV     kinetic energy spread (standard deviation) [MeV/u]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in] material_no     material code number
	@see          AT_DataMaterial.h for definition
	@param[in] eps             fraction of primary fluence contributing to the tail of energy spectrum
	if negative a default value of 0.03 is assumed
	@param[in] dose_drop       fraction of max dose at which range is calculated
	if negative a default value of 0.8 is assumed
	@param[in] search_direction   is positive a search is done in distal part (behind Bragg peak maximum), otherwise
	search is done in proximal part
	if negative a default value of 0.8 is assumed
	@return                    range [cm]
	"""
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_material_no__internal = p_material_no
	p_eps__internal = p_eps
	p_dose_drop__internal = p_dose_drop
	p_search_direction__internal = p_search_direction
	ret = _libAT.lib.AT_range_Bortfeld_cm(p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_eps__internal.encode() if type(p_eps__internal) is str else p_eps__internal
			,p_dose_drop__internal.encode() if type(p_dose_drop__internal) is str else p_dose_drop__internal
			,p_search_direction__internal.encode() if type(p_search_direction__internal) is str else p_search_direction__internal
			)
	return ret
	

def AT_fwhm_Bortfeld_cm(p_E_MeV, p_sigma_E_MeV, p_material_no, p_eps):
	"""
	Wrapping function generated for C language function documented as follows:
	Full width at half-maximum (FWHM) defined as the width of the dose profile at 50% of maximum dose value.
	@see AT_dose_Bortfeld_Gy_single for details of Bortfeld dose models
	@param[in] E_MeV           initial kinetic energy of proton beam [MeV/u]
	@param[in] sigma_E_MeV     kinetic energy spread (standard deviation) [MeV/u]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in] material_no     material code number
	@see          AT_DataMaterial.h for definition
	@param[in] eps             fraction of primary fluence contributing to the tail of energy spectrum
	if negative a default value of 0.03 is assumed
	@return                    FWHM [cm]
	"""
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_material_no__internal = p_material_no
	p_eps__internal = p_eps
	ret = _libAT.lib.AT_fwhm_Bortfeld_cm(p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_eps__internal.encode() if type(p_eps__internal) is str else p_eps__internal
			)
	return ret
	

def AT_max_plateau_Bortfeld(p_E_MeV, p_sigma_E_MeV, p_material_no, p_eps):
	"""
	Wrapping function generated for C language function documented as follows:
	Ratio between maximum dose value and the entrance dose (so called "max_to_plateau" ratio).
	@see AT_dose_Bortfeld_Gy_single for details of Bortfeld dose models
	@param[in] E_MeV           initial kinetic energy of proton beam [MeV/u]
	@param[in] sigma_E_MeV     kinetic energy spread (standard deviation) [MeV/u]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in] material_no     material code number
	@see          AT_DataMaterial.h for definition
	@param[in] eps             fraction of primary fluence contributing to the tail of energy spectrum
	if negative a default value of 0.03 is assumed
	@return                    "max_to_plateau" ratio
	"""
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_material_no__internal = p_material_no
	p_eps__internal = p_eps
	ret = _libAT.lib.AT_max_plateau_Bortfeld(p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_eps__internal.encode() if type(p_eps__internal) is str else p_eps__internal
			)
	return ret
	

def AT_fit_Bortfeld(p_range_cm, p_fwhm_cm, p_max_to_plateau, p_material_no, p_dose_drop, p_E_MeV, p_sigma_E_MeV, p_eps):
	"""
	Wrapping function generated for C language function documented as follows:
	@see AT_dose_Bortfeld_Gy_single for details of Bortfeld dose models
	@param[in] range_cm         range [cm]
	@param[in] fwhm_cm          FWHM [cm]
	@param[in] max_to_plateau   "max_to_plateau" ratio
	@param[in] material_no      material code number
	@see          AT_DataMaterial.h for definition
	@param[in] dose_drop        fraction of max dose at which range is calculated
	if negative a default value of 0.8 is assumed
	@param[out] E_MeV           initial kinetic energy of proton beam [MeV/u]
	@param[out] sigma_E_MeV     kinetic energy spread (standard deviation) [MeV/u]
	@param[out] eps             fraction of primary fluence contributing to the tail of energy spectrum
	"""
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_E_MeV)
	for in_array_argument in [p_E_MeV,p_sigma_E_MeV,p_eps]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_E_MeV)
	for in_array_argument in [p_E_MeV,p_sigma_E_MeV,p_eps]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_E_MeV, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_sigma_E_MeV, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_eps, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_E_MeV) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_E_MeV.clear()
		p_E_MeV += [0]
	
	if len(p_sigma_E_MeV) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_sigma_E_MeV.clear()
		p_sigma_E_MeV += [0]
	
	if len(p_eps) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_eps.clear()
		p_eps += [0]
	
	p_range_cm__internal = p_range_cm
	p_fwhm_cm__internal = p_fwhm_cm
	p_max_to_plateau__internal = p_max_to_plateau
	p_material_no__internal = p_material_no
	p_dose_drop__internal = p_dose_drop
	p_E_MeV__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_E_MeV):
		p_E_MeV__internal[i] = v
	
	p_sigma_E_MeV__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_sigma_E_MeV):
		p_sigma_E_MeV__internal[i] = v
	
	p_eps__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_eps):
		p_eps__internal[i] = v
	
	_libAT.lib.AT_fit_Bortfeld(p_range_cm__internal.encode() if type(p_range_cm__internal) is str else p_range_cm__internal
			,p_fwhm_cm__internal.encode() if type(p_fwhm_cm__internal) is str else p_fwhm_cm__internal
			,p_max_to_plateau__internal.encode() if type(p_max_to_plateau__internal) is str else p_max_to_plateau__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_dose_drop__internal.encode() if type(p_dose_drop__internal) is str else p_dose_drop__internal
			,p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_eps__internal.encode() if type(p_eps__internal) is str else p_eps__internal
			)
	for i,v in enumerate(p_E_MeV__internal):
		p_E_MeV[i] = v
	
	for i,v in enumerate(p_sigma_E_MeV__internal):
		p_sigma_E_MeV[i] = v
	
	for i,v in enumerate(p_eps__internal):
		p_eps[i] = v
	
	

def AT_n_bins_for_single_impact_local_dose_distrib(p_E_MeV_u, p_particle_no, p_material_no, p_rdd_model, p_rdd_parameter, p_er_model, p_N2, p_stopping_power_source_no):
	"""
	Wrapping function generated for C language function documented as follows:
	@brief Successive Convolution algorithm
	Computes the size of the array to hold the f1 (single impact) local dose distribution for a given field, rdd, er
	@param[in]  n                   number of particle types in the mixed particle field
	@param[in]  E_MeV_u             energy of particles in the mixed particle field (array of size n)
	@param[in]  particle_no         type of the particles in the mixed particle field (array of size n)
	@param[in]  material_no         index number for detector material
	@param[in]  rdd_model           index number for chosen radial dose distribution
	@param[in]  rdd_parameter       parameters for chosen radial dose distribution (array of size 4)
	@param[in]  er_model            index number for chosen electron-range model
	@param[in]  N2                  number of bins per factor of two in local dose array
	@param[in]  stopping_power_source_no  TODO
	@return number of bins to hold the f1 distribution
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_rdd_parameter]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_rdd_model__internal = p_rdd_model
	p_rdd_parameter__internal = p_rdd_parameter
	p_er_model__internal = p_er_model
	p_N2__internal = p_N2
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	ret = _libAT.lib.AT_n_bins_for_single_impact_local_dose_distrib(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_rdd_model__internal.encode() if type(p_rdd_model__internal) is str else p_rdd_model__internal
			,p_rdd_parameter__internal.encode() if type(p_rdd_parameter__internal) is str else p_rdd_parameter__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_N2__internal.encode() if type(p_N2__internal) is str else p_N2__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			)
	return ret
	

def AT_n_bins_for_low_fluence_local_dose_distribution(p_u, p_fluence_factor, p_N2, p_f1_d_Gy, p_f1_dd_Gy, p_f1, p_n_bins_f, p_u_start, p_n_convolutions):
	"""
	Wrapping function generated for C language function documented as follows:
	Estimates the size of the array to hold the resulting f local dose distribution for a given field, rdd, er
	Usually step 3 of the CPP-SC method
	@param[in]  u                   mean number of tracks contributing to the representative point
	@param[in]  fluence_factor      variable to tweak the total dose from the mixed field (rather than change the single components fluences)
	@param[in]  N2                  number of bins per factor of two in local dose array
	@param[in]  n_bins_f1           number of bins holding the f1 distribution (from AT_SC_get_f1_array_size)
	@param[in]  f1_d_Gy             bin midpoints for f1 (array of size n_bins_f1)
	@param[in]  f1_dd_Gy            bin width for f1 (array of size n_bins_f1)
	@param[in]  f1                  f1 values (array of size n_bins_f1)
	@param[out] n_bins_f            number of bins holding the resulting f local dose distribution
	@param[out] u_start             value for u to start convolutions with, between 0.001 and 0.002 where linearization of f into no and one impact is valid
	@param[out] n_convolutions      number of convolutions necessary to get from u_start to u (u = 2^n_convolutions * u_start)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_f1_d_Gy,p_f1_dd_Gy,p_f1]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n_bins_f1
	declared_in_arr_param_size__n_bins_f1 = len(p_f1_d_Gy)
	for in_array_argument in [p_f1_d_Gy,p_f1_dd_Gy,p_f1]:
		if len(in_array_argument) != declared_in_arr_param_size__n_bins_f1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_n_bins_f)
	for in_array_argument in [p_n_bins_f,p_u_start,p_n_convolutions]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_n_bins_f, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_u_start, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_n_convolutions, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_n_bins_f) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_n_bins_f.clear()
		p_n_bins_f += [0]
	
	if len(p_u_start) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_u_start.clear()
		p_u_start += [0]
	
	if len(p_n_convolutions) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_n_convolutions.clear()
		p_n_convolutions += [0]
	
	# Array sizes variables initialization:
	p_n_bins_f1 = len(p_f1_d_Gy)
	p_u__internal = p_u
	p_fluence_factor__internal = p_fluence_factor
	p_N2__internal = p_N2
	p_n_bins_f1__internal = p_n_bins_f1
	p_f1_d_Gy__internal = p_f1_d_Gy
	p_f1_dd_Gy__internal = p_f1_dd_Gy
	p_f1__internal = p_f1
	p_n_bins_f__internal = ffi.new("long[]", 1)
	for i,v in enumerate(p_n_bins_f):
		p_n_bins_f__internal[i] = v
	
	p_u_start__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_u_start):
		p_u_start__internal[i] = v
	
	p_n_convolutions__internal = ffi.new("long[]", 1)
	for i,v in enumerate(p_n_convolutions):
		p_n_convolutions__internal[i] = v
	
	_libAT.lib.AT_n_bins_for_low_fluence_local_dose_distribution(p_u__internal.encode() if type(p_u__internal) is str else p_u__internal
			,p_fluence_factor__internal.encode() if type(p_fluence_factor__internal) is str else p_fluence_factor__internal
			,p_N2__internal.encode() if type(p_N2__internal) is str else p_N2__internal
			,p_n_bins_f1__internal.encode() if type(p_n_bins_f1__internal) is str else p_n_bins_f1__internal
			,p_f1_d_Gy__internal.encode() if type(p_f1_d_Gy__internal) is str else p_f1_d_Gy__internal
			,p_f1_dd_Gy__internal.encode() if type(p_f1_dd_Gy__internal) is str else p_f1_dd_Gy__internal
			,p_f1__internal.encode() if type(p_f1__internal) is str else p_f1__internal
			,p_n_bins_f__internal.encode() if type(p_n_bins_f__internal) is str else p_n_bins_f__internal
			,p_u_start__internal.encode() if type(p_u_start__internal) is str else p_u_start__internal
			,p_n_convolutions__internal.encode() if type(p_n_convolutions__internal) is str else p_n_convolutions__internal
			)
	for i,v in enumerate(p_n_bins_f__internal):
		p_n_bins_f[i] = v
	
	for i,v in enumerate(p_u_start__internal):
		p_u_start[i] = v
	
	for i,v in enumerate(p_n_convolutions__internal):
		p_n_convolutions[i] = v
	
	

def AT_low_fluence_local_dose_distribution(p_N2, p_f1_d_Gy, p_f1_dd_Gy, p_f1, p_f_d_Gy, p_f_dd_Gy, p_f_start):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the (linearized) local dose distribution to start convolutions with, i.e. f at u_start
	TODO why is it f at u_start ? u_start is not used in function body
	Usually step 4 of the CPP-SC method
	@param[in]  n_bins_f1           number of bins holding the f1 distribution (from AT_SC_get_f1_array_size)
	@param[in]  N2                  number of bins per factor of two in local dose array
	@param[in]  f1_d_Gy             bin midpoints for f1 (array of size n_bins_f1)
	@param[in]  f1_dd_Gy            bin width for f1 (array of size n_bins_f1)
	@param[in]  f1                  f1 values (array of size n_bins_f1)
	@param[in]  n_bins_f            number of bins holding the resulting f local dose distribution (from AT_SC_get_f_array_size)
	@param[out] f_d_Gy              bin midpoints for f (array of size n_bins_f)
	@param[out] f_dd_Gy             bin widths for f (array of size n_bins_f)
	@param[out] f_start             f values to start with (array of size n_bins_f)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_f1_d_Gy,p_f1_dd_Gy,p_f1]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n_bins_f1
	declared_in_arr_param_size__n_bins_f1 = len(p_f1_d_Gy)
	for in_array_argument in [p_f1_d_Gy,p_f1_dd_Gy,p_f1]:
		if len(in_array_argument) != declared_in_arr_param_size__n_bins_f1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: n_bins_f
	declared_in_arr_param_size__n_bins_f = len(p_f_d_Gy)
	for in_array_argument in [p_f_d_Gy,p_f_dd_Gy,p_f_start]:
		if len(in_array_argument) != declared_in_arr_param_size__n_bins_f:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_n_bins_f1 = len(p_f1_d_Gy)
	p_n_bins_f = len(p_f_d_Gy)
	p_n_bins_f1__internal = p_n_bins_f1
	p_N2__internal = p_N2
	p_f1_d_Gy__internal = p_f1_d_Gy
	p_f1_dd_Gy__internal = p_f1_dd_Gy
	p_f1__internal = p_f1
	p_n_bins_f__internal = p_n_bins_f
	p_f_d_Gy__internal = ffi.new("double[]", p_n_bins_f)
	for i,v in enumerate(p_f_d_Gy):
		p_f_d_Gy__internal[i] = v
	
	p_f_dd_Gy__internal = ffi.new("double[]", p_n_bins_f)
	for i,v in enumerate(p_f_dd_Gy):
		p_f_dd_Gy__internal[i] = v
	
	p_f_start__internal = ffi.new("double[]", p_n_bins_f)
	for i,v in enumerate(p_f_start):
		p_f_start__internal[i] = v
	
	_libAT.lib.AT_low_fluence_local_dose_distribution(p_n_bins_f1__internal.encode() if type(p_n_bins_f1__internal) is str else p_n_bins_f1__internal
			,p_N2__internal.encode() if type(p_N2__internal) is str else p_N2__internal
			,p_f1_d_Gy__internal.encode() if type(p_f1_d_Gy__internal) is str else p_f1_d_Gy__internal
			,p_f1_dd_Gy__internal.encode() if type(p_f1_dd_Gy__internal) is str else p_f1_dd_Gy__internal
			,p_f1__internal.encode() if type(p_f1__internal) is str else p_f1__internal
			,p_n_bins_f__internal.encode() if type(p_n_bins_f__internal) is str else p_n_bins_f__internal
			,p_f_d_Gy__internal.encode() if type(p_f_d_Gy__internal) is str else p_f_d_Gy__internal
			,p_f_dd_Gy__internal.encode() if type(p_f_dd_Gy__internal) is str else p_f_dd_Gy__internal
			,p_f_start__internal.encode() if type(p_f_start__internal) is str else p_f_start__internal
			)
	for i,v in enumerate(p_f_d_Gy__internal):
		p_f_d_Gy[i] = v
	
	for i,v in enumerate(p_f_dd_Gy__internal):
		p_f_dd_Gy[i] = v
	
	for i,v in enumerate(p_f_start__internal):
		p_f_start[i] = v
	
	

def AT_SuccessiveConvolutions(p_final_mean_number_of_tracks_contrib, p_N2, p_n_bins_f_used, p_f_d_Gy, p_f_dd_Gy, p_f, p_f0, p_fdd, p_dfdd, p_d, p_write_output, p_shrink_tails, p_shrink_tails_under, p_adjust_N2):
	"""
	Wrapping function generated for C language function documented as follows:
	Routine to perform the convolutions from initial linearized local dose distribution f_start to resulting f
	as described by Kellerer, 1969. This is a to most extend a reimplementation of Kellerer's original FORTRAN IV code.
	Usually step 5 of the CPP-SC method
	@param[in]      final_mean_number_of_tracks_contrib                   value for u to start convolutions with, between 0.001 and 0.002 where linearization of f into no and one impact is valid (from AT_SC_get_f_array_size)
	@param[in]      n_bins              Size of arrays convolutions are performed on
	@param[in,out]  N2                  number of bins per factor of two in local dose array f_start, will return new value in case it was adjusted by the routine (higher resolution in case of high fluences)
	@param[in,out]  n_bins_f_used       in number of bins used for f_start, out number of bins used for resulting. As tails can be cut and N2 adjusted this is usually not the array size for f_d_Gy, f_dd_Gy, f but smaller (so entries 0 to n_bins_f_used-1 are used)
	@param[in,out]  f_d_Gy              bin midpoints for f (array of size n_bins)
	@param[in,out]  f_dd_Gy             bin widths for f (array of size n_bins)
	@param[in,out]  f                   in low fluence approx values to start with, out resulting values after convolutions (array of size n_bins)
	@param[out]     f0                  zero-dose f value (as bins are log this has to be separated)
	@param[out]     fdd                 frequency f x f_dd_Gy precomputed for comfort (array of size n_bins)
	@param[out]     dfdd                dose contribution f x f_dd_Gy precomputed for comfort (array of size n_bins)
	@param[out]     d                   first moment of distribution f - should coincide with given dose and provides check on convolution quality
	@param[in]      write_output        if true, a very verbose log file will be written ("SuccessiveConvolutions.log") with results from each convolution
	@param[in]      shrink_tails        if true, the upper and lower tail of f will be cut after every convolution (bins that contribute less than "shrink_tails_under" to the first moment @<d@>)
	@param[in]      shrink_tails_under  cut threshold for tails
	@param[in]      adjust_N2           if true, N2 (i.e. the bin density) can be adjusted. This can be necessary esp. for high doses or fluences where f gets very narrow
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_N2,p_n_bins_f_used,p_f_d_Gy,p_f_dd_Gy,p_f]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_N2)
	for in_array_argument in [p_N2,p_n_bins_f_used]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n_bins
	declared_in_arr_param_size__n_bins = len(p_f_d_Gy)
	for in_array_argument in [p_f_d_Gy,p_f_dd_Gy,p_f]:
		if len(in_array_argument) != declared_in_arr_param_size__n_bins:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_f0 is passed correctly:
	if len(p_f0) != len(p_n_bins_f_used):
		out_array_auto_init = "\nWarning: OUT array parameter p_f0 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_f0.clear()
		p_f0 += [0]*len(p_n_bins_f_used)
	
	# Procedure to check if OUT array p_fdd is passed correctly:
	if len(p_fdd) != len(p_f):
		out_array_auto_init = "\nWarning: OUT array parameter p_fdd was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_fdd.clear()
		p_fdd += [0]*len(p_f)
	
	# Procedure to check if OUT array p_dfdd is passed correctly:
	if len(p_dfdd) != len(p_f):
		out_array_auto_init = "\nWarning: OUT array parameter p_dfdd was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_dfdd.clear()
		p_dfdd += [0]*len(p_f)
	
	# Procedure to check if OUT array p_d is passed correctly:
	if len(p_d) != len(p_n_bins_f_used):
		out_array_auto_init = "\nWarning: OUT array parameter p_d was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_d.clear()
		p_d += [0]*len(p_n_bins_f_used)
	
	if not isinstance(p_N2, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_n_bins_f_used, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_f0, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_d, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_N2) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_N2.clear()
		p_N2 += [0]
	
	if len(p_n_bins_f_used) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_n_bins_f_used.clear()
		p_n_bins_f_used += [0]
	
	if len(p_f0) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_f0.clear()
		p_f0 += [0]
	
	if len(p_d) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_d.clear()
		p_d += [0]
	
	# Array sizes variables initialization:
	p_n_bins = len(p_f_d_Gy)
	p_final_mean_number_of_tracks_contrib__internal = p_final_mean_number_of_tracks_contrib
	p_n_bins__internal = p_n_bins
	p_N2__internal = ffi.new("long[]", 1)
	for i,v in enumerate(p_N2):
		p_N2__internal[i] = v
	
	p_n_bins_f_used__internal = ffi.new("long[]", 1)
	for i,v in enumerate(p_n_bins_f_used):
		p_n_bins_f_used__internal[i] = v
	
	p_f_d_Gy__internal = ffi.new("double[]", p_n_bins)
	for i,v in enumerate(p_f_d_Gy):
		p_f_d_Gy__internal[i] = v
	
	p_f_dd_Gy__internal = ffi.new("double[]", p_n_bins)
	for i,v in enumerate(p_f_dd_Gy):
		p_f_dd_Gy__internal[i] = v
	
	p_f__internal = ffi.new("double[]", p_n_bins)
	for i,v in enumerate(p_f):
		p_f__internal[i] = v
	
	p_f0__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_f0):
		p_f0__internal[i] = v
	
	p_fdd__internal = ffi.new("double[]", p_n_bins)
	for i,v in enumerate(p_fdd):
		p_fdd__internal[i] = v
	
	p_dfdd__internal = ffi.new("double[]", p_n_bins)
	for i,v in enumerate(p_dfdd):
		p_dfdd__internal[i] = v
	
	p_d__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_d):
		p_d__internal[i] = v
	
	p_write_output__internal = p_write_output
	p_shrink_tails__internal = p_shrink_tails
	p_shrink_tails_under__internal = p_shrink_tails_under
	p_adjust_N2__internal = p_adjust_N2
	_libAT.lib.AT_SuccessiveConvolutions(p_final_mean_number_of_tracks_contrib__internal.encode() if type(p_final_mean_number_of_tracks_contrib__internal) is str else p_final_mean_number_of_tracks_contrib__internal
			,p_n_bins__internal.encode() if type(p_n_bins__internal) is str else p_n_bins__internal
			,p_N2__internal.encode() if type(p_N2__internal) is str else p_N2__internal
			,p_n_bins_f_used__internal.encode() if type(p_n_bins_f_used__internal) is str else p_n_bins_f_used__internal
			,p_f_d_Gy__internal.encode() if type(p_f_d_Gy__internal) is str else p_f_d_Gy__internal
			,p_f_dd_Gy__internal.encode() if type(p_f_dd_Gy__internal) is str else p_f_dd_Gy__internal
			,p_f__internal.encode() if type(p_f__internal) is str else p_f__internal
			,p_f0__internal.encode() if type(p_f0__internal) is str else p_f0__internal
			,p_fdd__internal.encode() if type(p_fdd__internal) is str else p_fdd__internal
			,p_dfdd__internal.encode() if type(p_dfdd__internal) is str else p_dfdd__internal
			,p_d__internal.encode() if type(p_d__internal) is str else p_d__internal
			,p_write_output__internal.encode() if type(p_write_output__internal) is str else p_write_output__internal
			,p_shrink_tails__internal.encode() if type(p_shrink_tails__internal) is str else p_shrink_tails__internal
			,p_shrink_tails_under__internal.encode() if type(p_shrink_tails_under__internal) is str else p_shrink_tails_under__internal
			,p_adjust_N2__internal.encode() if type(p_adjust_N2__internal) is str else p_adjust_N2__internal
			)
	for i,v in enumerate(p_N2__internal):
		p_N2[i] = v
	
	for i,v in enumerate(p_n_bins_f_used__internal):
		p_n_bins_f_used[i] = v
	
	for i,v in enumerate(p_f_d_Gy__internal):
		p_f_d_Gy[i] = v
	
	for i,v in enumerate(p_f_dd_Gy__internal):
		p_f_dd_Gy[i] = v
	
	for i,v in enumerate(p_f__internal):
		p_f[i] = v
	
	for i,v in enumerate(p_f0__internal):
		p_f0[i] = v
	
	for i,v in enumerate(p_fdd__internal):
		p_fdd[i] = v
	
	for i,v in enumerate(p_dfdd__internal):
		p_dfdd[i] = v
	
	for i,v in enumerate(p_d__internal):
		p_d[i] = v
	
	

def AT_n_bins_for_DSB_distribution(p_n_bins_f, p_f_d_Gy, p_f_dd_Gy, p_f, p_enhancement_factor, p_DSB_per_Gy_per_domain):
	p_n_bins_f__internal = p_n_bins_f
	p_f_d_Gy__internal = p_f_d_Gy
	p_f_dd_Gy__internal = p_f_dd_Gy
	p_f__internal = p_f
	p_enhancement_factor__internal = p_enhancement_factor
	p_DSB_per_Gy_per_domain__internal = p_DSB_per_Gy_per_domain
	ret = _libAT.lib.AT_n_bins_for_DSB_distribution(p_n_bins_f__internal.encode() if type(p_n_bins_f__internal) is str else p_n_bins_f__internal
			,p_f_d_Gy__internal.encode() if type(p_f_d_Gy__internal) is str else p_f_d_Gy__internal
			,p_f_dd_Gy__internal.encode() if type(p_f_dd_Gy__internal) is str else p_f_dd_Gy__internal
			,p_f__internal.encode() if type(p_f__internal) is str else p_f__internal
			,p_enhancement_factor__internal.encode() if type(p_enhancement_factor__internal) is str else p_enhancement_factor__internal
			,p_DSB_per_Gy_per_domain__internal.encode() if type(p_DSB_per_Gy_per_domain__internal) is str else p_DSB_per_Gy_per_domain__internal
			)
	return ret
	

def AT_get_DSB_distribution(p_n_bins_f, p_f_d_Gy, p_f_dd_Gy, p_f, p_enhancement_factor, p_DSB_per_Gy_per_domain, p_domains_per_nucleus, p_max_number_of_DSBs, p_p_DSB, p_total_pDSBs, p_total_nDSBs, p_number_of_iDSBs, p_number_of_cDSBs, p_avg_number_of_DSBs_in_cDSBs):
	p_n_bins_f__internal = p_n_bins_f
	p_f_d_Gy__internal = p_f_d_Gy
	p_f_dd_Gy__internal = p_f_dd_Gy
	p_f__internal = p_f
	p_enhancement_factor__internal = p_enhancement_factor
	p_DSB_per_Gy_per_domain__internal = p_DSB_per_Gy_per_domain
	p_domains_per_nucleus__internal = p_domains_per_nucleus
	p_max_number_of_DSBs__internal = p_max_number_of_DSBs
	p_p_DSB__internal = ffi.new("double[]", len(p_p_DSB))
	for i,v in enumerate(p_p_DSB):
		p_p_DSB__internal[i] = v
	
	p_total_pDSBs__internal = ffi.new("double[]", len(p_total_pDSBs))
	for i,v in enumerate(p_total_pDSBs):
		p_total_pDSBs__internal[i] = v
	
	p_total_nDSBs__internal = ffi.new("double[]", len(p_total_nDSBs))
	for i,v in enumerate(p_total_nDSBs):
		p_total_nDSBs__internal[i] = v
	
	p_number_of_iDSBs__internal = ffi.new("double[]", len(p_number_of_iDSBs))
	for i,v in enumerate(p_number_of_iDSBs):
		p_number_of_iDSBs__internal[i] = v
	
	p_number_of_cDSBs__internal = ffi.new("double[]", len(p_number_of_cDSBs))
	for i,v in enumerate(p_number_of_cDSBs):
		p_number_of_cDSBs__internal[i] = v
	
	p_avg_number_of_DSBs_in_cDSBs__internal = ffi.new("double[]", len(p_avg_number_of_DSBs_in_cDSBs))
	for i,v in enumerate(p_avg_number_of_DSBs_in_cDSBs):
		p_avg_number_of_DSBs_in_cDSBs__internal[i] = v
	
	_libAT.lib.AT_get_DSB_distribution(p_n_bins_f__internal.encode() if type(p_n_bins_f__internal) is str else p_n_bins_f__internal
			,p_f_d_Gy__internal.encode() if type(p_f_d_Gy__internal) is str else p_f_d_Gy__internal
			,p_f_dd_Gy__internal.encode() if type(p_f_dd_Gy__internal) is str else p_f_dd_Gy__internal
			,p_f__internal.encode() if type(p_f__internal) is str else p_f__internal
			,p_enhancement_factor__internal.encode() if type(p_enhancement_factor__internal) is str else p_enhancement_factor__internal
			,p_DSB_per_Gy_per_domain__internal.encode() if type(p_DSB_per_Gy_per_domain__internal) is str else p_DSB_per_Gy_per_domain__internal
			,p_domains_per_nucleus__internal.encode() if type(p_domains_per_nucleus__internal) is str else p_domains_per_nucleus__internal
			,p_max_number_of_DSBs__internal.encode() if type(p_max_number_of_DSBs__internal) is str else p_max_number_of_DSBs__internal
			,p_p_DSB__internal.encode() if type(p_p_DSB__internal) is str else p_p_DSB__internal
			,p_total_pDSBs__internal.encode() if type(p_total_pDSBs__internal) is str else p_total_pDSBs__internal
			,p_total_nDSBs__internal.encode() if type(p_total_nDSBs__internal) is str else p_total_nDSBs__internal
			,p_number_of_iDSBs__internal.encode() if type(p_number_of_iDSBs__internal) is str else p_number_of_iDSBs__internal
			,p_number_of_cDSBs__internal.encode() if type(p_number_of_cDSBs__internal) is str else p_number_of_cDSBs__internal
			,p_avg_number_of_DSBs_in_cDSBs__internal.encode() if type(p_avg_number_of_DSBs_in_cDSBs__internal) is str else p_avg_number_of_DSBs_in_cDSBs__internal
			)
	for i,v in enumerate(p_p_DSB__internal):
		p_p_DSB[i] = v
	
	for i,v in enumerate(p_total_pDSBs__internal):
		p_total_pDSBs[i] = v
	
	for i,v in enumerate(p_total_nDSBs__internal):
		p_total_nDSBs[i] = v
	
	for i,v in enumerate(p_number_of_iDSBs__internal):
		p_number_of_iDSBs[i] = v
	
	for i,v in enumerate(p_number_of_cDSBs__internal):
		p_number_of_cDSBs[i] = v
	
	for i,v in enumerate(p_avg_number_of_DSBs_in_cDSBs__internal):
		p_avg_number_of_DSBs_in_cDSBs[i] = v
	
	

def AT_translate_dose_into_DSB_distribution(p_f_d_Gy, p_f_dd_Gy, p_f, p_enhancement_factor, p_DSB_per_Gy_per_domain, p_domains_per_nucleus, p_write_output, p_total_pDSBs, p_total_nDSBs, p_number_of_iDSBs, p_number_of_cDSBs, p_avg_number_of_DSBs_in_cDSBs):
	"""
	Wrapping function generated for C language function documented as follows:
	Converts a local dose into a DSB distribution assuming
	Poissonian rule for creation.
	@param[in]      n_bins_f                   		number of bins for local dose distribution
	@param[in]      f_d_Gy              				bin midpoints for f (array of size n_bins_f)
	@param[in]      f_dd_Gy                  		bin widths for f (array of size n_bins_f)
	@param[in]      f       							dose frequency (array of size n_bins_f)
	@param[in]      enhancement_factor              	dose enhancement factor (array of size n_bins_f)
	@param[in]      DSB_per_Gy_per_domain            number of DSBs per domain per Gy
	@param[in]      domains_per_nucleus              number of domains in nucleus
	@param[in]      write_output                  	if true, a log file will be written ("dose_to_DSBs.log") containing the DBS distribution
	@param[out]     total_pDSBs                 		probability sum of DSB probability (quality check, has to be ~1)
	@param[out]     total_nDSBs                		number of DSBs in nucleus
	@param[out]     number_of_iDSBs                  number of isolated DSBs in nucleus
	@param[out]     number_of_cDSBs        			number of complex DSBs in nucleus
	@param[out]     avg_number_of_DSBs_in_cDSBs		average number of DSBs in complex DSBs
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_f_d_Gy,p_f_dd_Gy,p_f,p_enhancement_factor]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n_bins_f
	declared_in_arr_param_size__n_bins_f = len(p_f_d_Gy)
	for in_array_argument in [p_f_d_Gy,p_f_dd_Gy,p_f,p_enhancement_factor]:
		if len(in_array_argument) != declared_in_arr_param_size__n_bins_f:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_total_pDSBs)
	for in_array_argument in [p_total_pDSBs,p_total_nDSBs,p_number_of_iDSBs,p_number_of_cDSBs,p_avg_number_of_DSBs_in_cDSBs]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_total_pDSBs, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_total_nDSBs, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_number_of_iDSBs, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_number_of_cDSBs, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_avg_number_of_DSBs_in_cDSBs, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_total_pDSBs) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_total_pDSBs.clear()
		p_total_pDSBs += [0]
	
	if len(p_total_nDSBs) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_total_nDSBs.clear()
		p_total_nDSBs += [0]
	
	if len(p_number_of_iDSBs) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_number_of_iDSBs.clear()
		p_number_of_iDSBs += [0]
	
	if len(p_number_of_cDSBs) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_number_of_cDSBs.clear()
		p_number_of_cDSBs += [0]
	
	if len(p_avg_number_of_DSBs_in_cDSBs) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_avg_number_of_DSBs_in_cDSBs.clear()
		p_avg_number_of_DSBs_in_cDSBs += [0]
	
	# Array sizes variables initialization:
	p_n_bins_f = len(p_f_d_Gy)
	p_n_bins_f__internal = p_n_bins_f
	p_f_d_Gy__internal = p_f_d_Gy
	p_f_dd_Gy__internal = p_f_dd_Gy
	p_f__internal = p_f
	p_enhancement_factor__internal = p_enhancement_factor
	p_DSB_per_Gy_per_domain__internal = p_DSB_per_Gy_per_domain
	p_domains_per_nucleus__internal = p_domains_per_nucleus
	p_write_output__internal = p_write_output
	p_total_pDSBs__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_total_pDSBs):
		p_total_pDSBs__internal[i] = v
	
	p_total_nDSBs__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_total_nDSBs):
		p_total_nDSBs__internal[i] = v
	
	p_number_of_iDSBs__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_number_of_iDSBs):
		p_number_of_iDSBs__internal[i] = v
	
	p_number_of_cDSBs__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_number_of_cDSBs):
		p_number_of_cDSBs__internal[i] = v
	
	p_avg_number_of_DSBs_in_cDSBs__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_avg_number_of_DSBs_in_cDSBs):
		p_avg_number_of_DSBs_in_cDSBs__internal[i] = v
	
	_libAT.lib.AT_translate_dose_into_DSB_distribution(p_n_bins_f__internal.encode() if type(p_n_bins_f__internal) is str else p_n_bins_f__internal
			,p_f_d_Gy__internal.encode() if type(p_f_d_Gy__internal) is str else p_f_d_Gy__internal
			,p_f_dd_Gy__internal.encode() if type(p_f_dd_Gy__internal) is str else p_f_dd_Gy__internal
			,p_f__internal.encode() if type(p_f__internal) is str else p_f__internal
			,p_enhancement_factor__internal.encode() if type(p_enhancement_factor__internal) is str else p_enhancement_factor__internal
			,p_DSB_per_Gy_per_domain__internal.encode() if type(p_DSB_per_Gy_per_domain__internal) is str else p_DSB_per_Gy_per_domain__internal
			,p_domains_per_nucleus__internal.encode() if type(p_domains_per_nucleus__internal) is str else p_domains_per_nucleus__internal
			,p_write_output__internal.encode() if type(p_write_output__internal) is str else p_write_output__internal
			,p_total_pDSBs__internal.encode() if type(p_total_pDSBs__internal) is str else p_total_pDSBs__internal
			,p_total_nDSBs__internal.encode() if type(p_total_nDSBs__internal) is str else p_total_nDSBs__internal
			,p_number_of_iDSBs__internal.encode() if type(p_number_of_iDSBs__internal) is str else p_number_of_iDSBs__internal
			,p_number_of_cDSBs__internal.encode() if type(p_number_of_cDSBs__internal) is str else p_number_of_cDSBs__internal
			,p_avg_number_of_DSBs_in_cDSBs__internal.encode() if type(p_avg_number_of_DSBs_in_cDSBs__internal) is str else p_avg_number_of_DSBs_in_cDSBs__internal
			)
	for i,v in enumerate(p_total_pDSBs__internal):
		p_total_pDSBs[i] = v
	
	for i,v in enumerate(p_total_nDSBs__internal):
		p_total_nDSBs[i] = v
	
	for i,v in enumerate(p_number_of_iDSBs__internal):
		p_number_of_iDSBs[i] = v
	
	for i,v in enumerate(p_number_of_cDSBs__internal):
		p_number_of_cDSBs[i] = v
	
	for i,v in enumerate(p_avg_number_of_DSBs_in_cDSBs__internal):
		p_avg_number_of_DSBs_in_cDSBs[i] = v
	
	

def AT_KatzModel_inactivation_probability(p_r_m, p_E_MeV_u, p_particle_no, p_rdd_model, p_rdd_parameters, p_er_model, p_gamma_parameters, p_stop_power_source, p_inactivation_probability):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in] n                             todo
	@param[in] r_m                           todo (array of size n)
	@param[in] E_MeV_u                       todo
	@param[in] particle_no                   todo
	@param[in] rdd_model                     todo
	@param[in] rdd_parameters                todo (array of size 4)
	@param[in] er_model                      todo
	@param[in] gamma_parameters              todo (array of size 5)
	@param[in] stop_power_source             todo
	@param[out] inactivation_probability     results (array of size n)
	@return status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_r_m,p_rdd_parameters,p_gamma_parameters]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_inactivation_probability is passed correctly:
	if len(p_inactivation_probability) != len(p_r_m):
		out_array_auto_init = "\nWarning: OUT array parameter p_inactivation_probability was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_inactivation_probability.clear()
		p_inactivation_probability += [0]*len(p_r_m)
	
	# Array sizes variables initialization:
	p_n = len(p_r_m)
	p_n__internal = p_n
	p_r_m__internal = p_r_m
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_rdd_model__internal = p_rdd_model
	p_rdd_parameters__internal = p_rdd_parameters
	p_er_model__internal = p_er_model
	p_gamma_parameters__internal = p_gamma_parameters
	p_stop_power_source__internal = p_stop_power_source
	p_inactivation_probability__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_inactivation_probability):
		p_inactivation_probability__internal[i] = v
	
	ret = _libAT.lib.AT_KatzModel_inactivation_probability(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_r_m__internal.encode() if type(p_r_m__internal) is str else p_r_m__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_rdd_model__internal.encode() if type(p_rdd_model__internal) is str else p_rdd_model__internal
			,p_rdd_parameters__internal.encode() if type(p_rdd_parameters__internal) is str else p_rdd_parameters__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_gamma_parameters__internal.encode() if type(p_gamma_parameters__internal) is str else p_gamma_parameters__internal
			,p_stop_power_source__internal.encode() if type(p_stop_power_source__internal) is str else p_stop_power_source__internal
			,p_inactivation_probability__internal.encode() if type(p_inactivation_probability__internal) is str else p_inactivation_probability__internal
			)
	for i,v in enumerate(p_inactivation_probability__internal):
		p_inactivation_probability[i] = v
	
	return ret
	

def AT_KatzModel_mixed_field_survival(p_fluence_cm2, p_E_MeV_u, p_particle_no, p_rdd_model, p_rdd_parameters, p_er_model, p_D0_Gy, p_m, p_sigma0_m2, p_use_approximation, p_kappa, p_stopping_power_source_no, p_survival):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in] number_of_items           TODO
	@param[in] fluence_cm2               TODO (array of size number_of_items)
	@param[in] E_MeV_u                   TODO (array of size number_of_items)
	@param[in] particle_no               TODO (array of size number_of_items)
	@param[in] rdd_model                 TODO
	@param[in] rdd_parameters            TODO (array of size 4)
	@param[in] er_model                  TODO
	@param[in] D0_Gy TODO
	@param[in] m       TODO
	@param[in] sigma0_m2                 TODO
	@param[in] use_approximation         TODO
	@param[in] kappa                     TODO
	@param[in] stopping_power_source_no  TODO
	@param[out] survival                 TODO
	@return status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_fluence_cm2,p_E_MeV_u,p_particle_no,p_rdd_parameters]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_items
	declared_in_arr_param_size__number_of_items = len(p_fluence_cm2)
	for in_array_argument in [p_fluence_cm2,p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_items:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_survival, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_survival) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_survival.clear()
		p_survival += [0]
	
	# Array sizes variables initialization:
	p_number_of_items = len(p_fluence_cm2)
	p_number_of_items__internal = p_number_of_items
	p_fluence_cm2__internal = p_fluence_cm2
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_rdd_model__internal = p_rdd_model
	p_rdd_parameters__internal = p_rdd_parameters
	p_er_model__internal = p_er_model
	p_D0_Gy__internal = p_D0_Gy
	p_m__internal = p_m
	p_sigma0_m2__internal = p_sigma0_m2
	p_use_approximation__internal = p_use_approximation
	p_kappa__internal = p_kappa
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_survival__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_survival):
		p_survival__internal[i] = v
	
	ret = _libAT.lib.AT_KatzModel_mixed_field_survival(p_number_of_items__internal.encode() if type(p_number_of_items__internal) is str else p_number_of_items__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_rdd_model__internal.encode() if type(p_rdd_model__internal) is str else p_rdd_model__internal
			,p_rdd_parameters__internal.encode() if type(p_rdd_parameters__internal) is str else p_rdd_parameters__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_D0_Gy__internal.encode() if type(p_D0_Gy__internal) is str else p_D0_Gy__internal
			,p_m__internal.encode() if type(p_m__internal) is str else p_m__internal
			,p_sigma0_m2__internal.encode() if type(p_sigma0_m2__internal) is str else p_sigma0_m2__internal
			,p_use_approximation__internal.encode() if type(p_use_approximation__internal) is str else p_use_approximation__internal
			,p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_survival__internal.encode() if type(p_survival__internal) is str else p_survival__internal
			)
	for i,v in enumerate(p_survival__internal):
		p_survival[i] = v
	
	return ret
	

def AT_mean_energy_loss_keV(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	"""
	Wrapping function generated for C language function documented as follows:
	@brief Stopping power
	Computes the mean energy loss in a slab of
	material using the Bethe formula
	for many particles according to ICRU49
	BUT WITHOUT shell, Bloch or Barkas correction!
	No effective projectile charge is considered!
	@param[in]  	   E_MeV_u      energies of particle per nucleon
	@param[in]  	   particle_no  particle indices
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um
	@return     result
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_mean_energy_loss_keV(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_xi_keV(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	"""
	Wrapping function generated for C language function documented as follows:
	Parameter xi - reduced mean energy loss
	@param[in]  	   E_MeV_u      energies of particle per nucleon
	@param[in]  	   particle_no  particle indices
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um
	@return			xi
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_xi_keV(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_kappa_multi(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_kappa):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the kappa criterium for the
	energy loss distribution according to
	Seltzer and Berger, and CERN W5013
	No effective projectile charge is considered!
	@param[in]  	   n      				number of particles
	@param[in]  	   E_MeV_u      		energy of particle per amu (array of size n)
	@param[in]  	   particle_no  		particle index (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um (array of size n)
	@param[out]	   kappa				kappa parameter (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_kappa is passed correctly:
	if len(p_kappa) != len(p_slab_thickness_um):
		out_array_auto_init = "\nWarning: OUT array parameter p_kappa was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_kappa.clear()
		p_kappa += [0]*len(p_slab_thickness_um)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_kappa__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_kappa):
		p_kappa__internal[i] = v
	
	_libAT.lib.AT_kappa_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			)
	for i,v in enumerate(p_kappa__internal):
		p_kappa[i] = v
	
	

def AT_kappa_single(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param E_MeV_u
	@param particle_no
	@param material_no
	@param slab_thickness_um
	@return
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_kappa_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_Landau_PDF(p_lambda_landau, p_density):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the Landau probability density function using CERNLIB (G115)
	@param[in]  n                    array size
	@param[in]  lambda_landau        Landau lambda (array of size n)
	@param[out] density              resulting density (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_lambda_landau]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_density is passed correctly:
	if len(p_density) != len(p_lambda_landau):
		out_array_auto_init = "\nWarning: OUT array parameter p_density was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_density.clear()
		p_density += [0]*len(p_lambda_landau)
	
	# Array sizes variables initialization:
	p_n = len(p_lambda_landau)
	p_n__internal = p_n
	p_lambda_landau__internal = p_lambda_landau
	p_density__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_density):
		p_density__internal[i] = v
	
	_libAT.lib.AT_Landau_PDF(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_lambda_landau__internal.encode() if type(p_lambda_landau__internal) is str else p_lambda_landau__internal
			,p_density__internal.encode() if type(p_density__internal) is str else p_density__internal
			)
	for i,v in enumerate(p_density__internal):
		p_density[i] = v
	
	

def AT_Landau_IDF(p_rnd, p_lambda_landau):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the Landau inverse distribution function using CERNLIB (G115)
	@param[in]  n                    array size
	@param[in]  rnd                  random number from uniform distribution between 0 and 1 (array of size n)
	@param[out] lambda_landau        resulting Landau lambda (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_rnd]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_lambda_landau is passed correctly:
	if len(p_lambda_landau) != len(p_rnd):
		out_array_auto_init = "\nWarning: OUT array parameter p_lambda_landau was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_lambda_landau.clear()
		p_lambda_landau += [0]*len(p_rnd)
	
	# Array sizes variables initialization:
	p_n = len(p_rnd)
	p_n__internal = p_n
	p_rnd__internal = p_rnd
	p_lambda_landau__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_lambda_landau):
		p_lambda_landau__internal[i] = v
	
	_libAT.lib.AT_Landau_IDF(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_rnd__internal.encode() if type(p_rnd__internal) is str else p_rnd__internal
			,p_lambda_landau__internal.encode() if type(p_lambda_landau__internal) is str else p_lambda_landau__internal
			)
	for i,v in enumerate(p_lambda_landau__internal):
		p_lambda_landau[i] = v
	
	

def AT_lambda_landau_from_energy_loss_multi(p_energy_loss_keV, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_lambda_landau):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the lambda parameter for the
	Landau distribution acc. to CERN W5013
	No effective projectile charge is considered!
	@param[in]  	   n      				number of energy loss data
	@param[in]  	   energy_loss_keV      energy loss (array of size n)
	@param[in]  	   E_MeV_u      		energy of particle per nucleon
	@param[in]  	   particle_no  		particle index
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um
	@param[out]     lambda_landau (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_energy_loss_keV]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_lambda_landau is passed correctly:
	if len(p_lambda_landau) != len(p_energy_loss_keV):
		out_array_auto_init = "\nWarning: OUT array parameter p_lambda_landau was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_lambda_landau.clear()
		p_lambda_landau += [0]*len(p_energy_loss_keV)
	
	# Array sizes variables initialization:
	p_n = len(p_energy_loss_keV)
	p_n__internal = p_n
	p_energy_loss_keV__internal = p_energy_loss_keV
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_lambda_landau__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_lambda_landau):
		p_lambda_landau__internal[i] = v
	
	_libAT.lib.AT_lambda_landau_from_energy_loss_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_energy_loss_keV__internal.encode() if type(p_energy_loss_keV__internal) is str else p_energy_loss_keV__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_lambda_landau__internal.encode() if type(p_lambda_landau__internal) is str else p_lambda_landau__internal
			)
	for i,v in enumerate(p_lambda_landau__internal):
		p_lambda_landau[i] = v
	
	

def AT_lambda_landau_from_energy_loss_single(p_energy_loss_keV, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	"""
	Wrapping function generated for C language function documented as follows:
	@param[in]  	   energy_loss_keV          TODO
	@param[in]  E_MeV_u      energy of particle per nucleon [MeV/u]
	@param[in]  particle_no  type of the particles
	@see          AT_DataParticle.h for definition
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  	   slab_thickness_um     	TODO
	@return
	"""
	p_energy_loss_keV__internal = p_energy_loss_keV
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_lambda_landau_from_energy_loss_single(p_energy_loss_keV__internal.encode() if type(p_energy_loss_keV__internal) is str else p_energy_loss_keV__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_lambda_mean_multi(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_lambda_mean):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the mean lambda, introduced to enable
	average value for Landau distribution. See Geant3 W5013, p.254
	@param[in]  	   n      				number of particles
	@param[in]  	   E_MeV_u      		energy of particle per amu (array of size n)
	@param[in]  	   particle_no  		particle index (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um (array of size n)
	@param[out]	   lambda_mean			mean lambda for given particle (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_lambda_mean is passed correctly:
	if len(p_lambda_mean) != len(p_slab_thickness_um):
		out_array_auto_init = "\nWarning: OUT array parameter p_lambda_mean was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_lambda_mean.clear()
		p_lambda_mean += [0]*len(p_slab_thickness_um)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_lambda_mean__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_lambda_mean):
		p_lambda_mean__internal[i] = v
	
	_libAT.lib.AT_lambda_mean_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_lambda_mean__internal.encode() if type(p_lambda_mean__internal) is str else p_lambda_mean__internal
			)
	for i,v in enumerate(p_lambda_mean__internal):
		p_lambda_mean[i] = v
	
	

def AT_lambda_mean_single(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_lambda_mean_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_lambda_max_multi(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_lambda_max):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the mean lambda, introduced to enable
	average value for Landau distribution. See Geant3 W5013, p.254
	@param[in]  	   n      				number of particles
	@param[in]  	   E_MeV_u      		energy of particle per amu (array of size n)
	@param[in]  	   particle_no  		particle index (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um (array of size n)
	@param[out]	   lambda_max			maximum lambda for given particle (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_lambda_max is passed correctly:
	if len(p_lambda_max) != len(p_slab_thickness_um):
		out_array_auto_init = "\nWarning: OUT array parameter p_lambda_max was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_lambda_max.clear()
		p_lambda_max += [0]*len(p_slab_thickness_um)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_lambda_max__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_lambda_max):
		p_lambda_max__internal[i] = v
	
	_libAT.lib.AT_lambda_max_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_lambda_max__internal.encode() if type(p_lambda_max__internal) is str else p_lambda_max__internal
			)
	for i,v in enumerate(p_lambda_max__internal):
		p_lambda_max[i] = v
	
	

def AT_lambda_max_single(p_lambda_mean):
	p_lambda_mean__internal = p_lambda_mean
	ret = _libAT.lib.AT_lambda_max_single(p_lambda_mean__internal.encode() if type(p_lambda_mean__internal) is str else p_lambda_mean__internal
			)
	return ret
	

def AT_lambda_Landau_Mode():
	ret = _libAT.lib.AT_lambda_Landau_Mode()
	return ret
	

def AT_lambda_Landau_Mean(p_kappa, p_beta):
	p_kappa__internal = p_kappa
	p_beta__internal = p_beta
	ret = _libAT.lib.AT_lambda_Landau_Mean(p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			)
	return ret
	

def AT_lambda_Landau_FWHM():
	ret = _libAT.lib.AT_lambda_Landau_FWHM()
	return ret
	

def AT_energy_loss_keV_Landau_FWHM(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_energy_loss_keV_Landau_FWHM(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_energy_loss_keV_Landau_Mode(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_energy_loss_keV_Landau_Mode(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_energy_loss_from_lambda_landau_multi(p_lambda_landau, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_energy_loss_keV):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the energy loss from the lambda parameter
	of the Landau distribution acc. to CERN W5013
	No effective projectile charge is considered!
	@param[in]  	   n      				number of energy loss data
	@param[in]  	   lambda_landau      Landau lambda (array of size n)
	@param[in]  	   E_MeV_u      		energy of particle per nucleon (array of size n)
	@param[in]  	   particle_no  		particle index (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um (array of size n)
	@param[out]     energy_loss_keV (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_lambda_landau,p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_lambda_landau)
	for in_array_argument in [p_lambda_landau,p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_energy_loss_keV is passed correctly:
	if len(p_energy_loss_keV) != len(p_slab_thickness_um):
		out_array_auto_init = "\nWarning: OUT array parameter p_energy_loss_keV was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_energy_loss_keV.clear()
		p_energy_loss_keV += [0]*len(p_slab_thickness_um)
	
	# Array sizes variables initialization:
	p_n = len(p_lambda_landau)
	p_n__internal = p_n
	p_lambda_landau__internal = p_lambda_landau
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_energy_loss_keV__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_energy_loss_keV):
		p_energy_loss_keV__internal[i] = v
	
	_libAT.lib.AT_energy_loss_from_lambda_landau_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_lambda_landau__internal.encode() if type(p_lambda_landau__internal) is str else p_lambda_landau__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_energy_loss_keV__internal.encode() if type(p_energy_loss_keV__internal) is str else p_energy_loss_keV__internal
			)
	for i,v in enumerate(p_energy_loss_keV__internal):
		p_energy_loss_keV[i] = v
	
	

def AT_energy_loss_from_lambda_landau_single(p_lambda_landau, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	p_lambda_landau__internal = p_lambda_landau
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_energy_loss_from_lambda_landau_single(p_lambda_landau__internal.encode() if type(p_lambda_landau__internal) is str else p_lambda_landau__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_Landau_energy_loss_distribution(p_energy_loss_keV, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_fDdD):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the energy loss
	Landau distribution acc. to CERN W5013
	No effective projectile charge is considered!
	@param[in]  	   n      				number of energy loss data
	@param[in]  	   energy_loss_keV      energy loss (array of size n)
	@param[in]  	   E_MeV_u      		energy of particle per nucleon
	@param[in]  	   particle_no  		particle index
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um
	@param[out]     fDdD (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_energy_loss_keV]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_fDdD is passed correctly:
	if len(p_fDdD) != len(p_energy_loss_keV):
		out_array_auto_init = "\nWarning: OUT array parameter p_fDdD was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_fDdD.clear()
		p_fDdD += [0]*len(p_energy_loss_keV)
	
	# Array sizes variables initialization:
	p_n = len(p_energy_loss_keV)
	p_n__internal = p_n
	p_energy_loss_keV__internal = p_energy_loss_keV
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_fDdD__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_fDdD):
		p_fDdD__internal[i] = v
	
	_libAT.lib.AT_Landau_energy_loss_distribution(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_energy_loss_keV__internal.encode() if type(p_energy_loss_keV__internal) is str else p_energy_loss_keV__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_fDdD__internal.encode() if type(p_fDdD__internal) is str else p_fDdD__internal
			)
	for i,v in enumerate(p_fDdD__internal):
		p_fDdD[i] = v
	
	

def AT_Vavilov_PDF(p_lambda_vavilov, p_kappa, p_beta, p_density):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the Vavilov probability density function using CERNLIB (G116)
	@param[in]  n                   array size
	@param[in]  lambda_vavilov      Vavilov lambda (array of size n)
	@param[in]  kappa               straggling parameter
	@param[in]  beta                relativistic speed, between 0 and 1
	@param[out] density             resulting density (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_lambda_vavilov]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_density is passed correctly:
	if len(p_density) != len(p_lambda_vavilov):
		out_array_auto_init = "\nWarning: OUT array parameter p_density was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_density.clear()
		p_density += [0]*len(p_lambda_vavilov)
	
	# Array sizes variables initialization:
	p_n = len(p_lambda_vavilov)
	p_n__internal = p_n
	p_lambda_vavilov__internal = p_lambda_vavilov
	p_kappa__internal = p_kappa
	p_beta__internal = p_beta
	p_density__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_density):
		p_density__internal[i] = v
	
	_libAT.lib.AT_Vavilov_PDF(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_lambda_vavilov__internal.encode() if type(p_lambda_vavilov__internal) is str else p_lambda_vavilov__internal
			,p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			,p_density__internal.encode() if type(p_density__internal) is str else p_density__internal
			)
	for i,v in enumerate(p_density__internal):
		p_density[i] = v
	
	

def AT_Vavilov_IDF(p_rnd, p_kappa, p_beta, p_lambda_vavilov):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the Vavilov probability density function using CERNLIB (G116)
	@param[in]  n                   array size
	@param[in]  rnd                 random number from uniform distribution between 0 and 1 (array of size n)
	@param[in]  kappa               straggling parameter  (array of size n)
	@param[in]  beta                relativistic speed, between 0 and 1 (array of size n)
	@param[out] lambda_vavilov      resulting Vavilov lambda (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_rnd,p_kappa,p_beta]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_rnd)
	for in_array_argument in [p_rnd,p_kappa,p_beta]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_lambda_vavilov is passed correctly:
	if len(p_lambda_vavilov) != len(p_beta):
		out_array_auto_init = "\nWarning: OUT array parameter p_lambda_vavilov was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_lambda_vavilov.clear()
		p_lambda_vavilov += [0]*len(p_beta)
	
	# Array sizes variables initialization:
	p_n = len(p_rnd)
	p_n__internal = p_n
	p_rnd__internal = p_rnd
	p_kappa__internal = p_kappa
	p_beta__internal = p_beta
	p_lambda_vavilov__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_lambda_vavilov):
		p_lambda_vavilov__internal[i] = v
	
	_libAT.lib.AT_Vavilov_IDF(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_rnd__internal.encode() if type(p_rnd__internal) is str else p_rnd__internal
			,p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			,p_lambda_vavilov__internal.encode() if type(p_lambda_vavilov__internal) is str else p_lambda_vavilov__internal
			)
	for i,v in enumerate(p_lambda_vavilov__internal):
		p_lambda_vavilov[i] = v
	
	

def AT_lambda_vavilov_from_energy_loss_multi(p_energy_loss_keV, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_lambda_vavilov):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the lambda parameter for the
	Vavilov distribution acc. to CERN W5013
	No effective projectile charge is considered!
	@param[in]  	   n      				number of energy loss data
	@param[in]  	   energy_loss_keV      energy loss (array of size n)
	@param[in]  	   E_MeV_u      		energy of particle per nucleon
	@param[in]  	   particle_no  		particle index
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um
	@param[out]     lambda_vavilov (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_energy_loss_keV]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_lambda_vavilov is passed correctly:
	if len(p_lambda_vavilov) != len(p_energy_loss_keV):
		out_array_auto_init = "\nWarning: OUT array parameter p_lambda_vavilov was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_lambda_vavilov.clear()
		p_lambda_vavilov += [0]*len(p_energy_loss_keV)
	
	# Array sizes variables initialization:
	p_n = len(p_energy_loss_keV)
	p_n__internal = p_n
	p_energy_loss_keV__internal = p_energy_loss_keV
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_lambda_vavilov__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_lambda_vavilov):
		p_lambda_vavilov__internal[i] = v
	
	_libAT.lib.AT_lambda_vavilov_from_energy_loss_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_energy_loss_keV__internal.encode() if type(p_energy_loss_keV__internal) is str else p_energy_loss_keV__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_lambda_vavilov__internal.encode() if type(p_lambda_vavilov__internal) is str else p_lambda_vavilov__internal
			)
	for i,v in enumerate(p_lambda_vavilov__internal):
		p_lambda_vavilov[i] = v
	
	

def AT_lambda_vavilov_from_energy_loss_single(p_energy_loss_keV, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	"""
	Wrapping function generated for C language function documented as follows:
	@param[in]  	   energy_loss_keV          TODO
	@param[in]  E_MeV_u      energy of particle per nucleon [MeV/u]
	@param[in]  particle_no  type of the particles
	@see          AT_DataParticle.h for definition
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  	   slab_thickness_um     	TODO
	@return
	"""
	p_energy_loss_keV__internal = p_energy_loss_keV
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_lambda_vavilov_from_energy_loss_single(p_energy_loss_keV__internal.encode() if type(p_energy_loss_keV__internal) is str else p_energy_loss_keV__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_lambda_Vavilov_Mode(p_kappa, p_beta):
	p_kappa__internal = p_kappa
	p_beta__internal = p_beta
	ret = _libAT.lib.AT_lambda_Vavilov_Mode(p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			)
	return ret
	

def AT_lambda_Vavilov_Mean(p_kappa, p_beta):
	p_kappa__internal = p_kappa
	p_beta__internal = p_beta
	ret = _libAT.lib.AT_lambda_Vavilov_Mean(p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			)
	return ret
	

def AT_lambda_Vavilov_Variance(p_kappa, p_beta):
	p_kappa__internal = p_kappa
	p_beta__internal = p_beta
	ret = _libAT.lib.AT_lambda_Vavilov_Variance(p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			)
	return ret
	

def AT_lambda_Vavilov_Skewness(p_kappa, p_beta):
	p_kappa__internal = p_kappa
	p_beta__internal = p_beta
	ret = _libAT.lib.AT_lambda_Vavilov_Skewness(p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			)
	return ret
	

def AT_lambda_Vavilov_FWHM(p_kappa, p_beta):
	p_kappa__internal = p_kappa
	p_beta__internal = p_beta
	ret = _libAT.lib.AT_lambda_Vavilov_FWHM(p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			)
	return ret
	

def AT_energy_loss_keV_Vavilov_FWHM(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_energy_loss_keV_Vavilov_FWHM(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_energy_loss_from_lambda_vavilov_multi(p_lambda_vavilov, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_energy_loss_keV):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the energy loss from the lambda parameter of the
	Vavilov distribution acc. to CERN W5013
	No effective projectile charge is considered!
	@param[in]  	   n      				number of energy loss data
	@param[in]  	   lambda_vavilov      Vavilov lambda (array of size n)
	@param[in]  	   E_MeV_u      		energy of particle per nucleon (array of size n)
	@param[in]  	   particle_no  		particle index (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um (array of size n)
	@param[out]     energy_loss_keV (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_lambda_vavilov,p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_lambda_vavilov)
	for in_array_argument in [p_lambda_vavilov,p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_energy_loss_keV is passed correctly:
	if len(p_energy_loss_keV) != len(p_slab_thickness_um):
		out_array_auto_init = "\nWarning: OUT array parameter p_energy_loss_keV was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_energy_loss_keV.clear()
		p_energy_loss_keV += [0]*len(p_slab_thickness_um)
	
	# Array sizes variables initialization:
	p_n = len(p_lambda_vavilov)
	p_n__internal = p_n
	p_lambda_vavilov__internal = p_lambda_vavilov
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_energy_loss_keV__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_energy_loss_keV):
		p_energy_loss_keV__internal[i] = v
	
	_libAT.lib.AT_energy_loss_from_lambda_vavilov_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_lambda_vavilov__internal.encode() if type(p_lambda_vavilov__internal) is str else p_lambda_vavilov__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_energy_loss_keV__internal.encode() if type(p_energy_loss_keV__internal) is str else p_energy_loss_keV__internal
			)
	for i,v in enumerate(p_energy_loss_keV__internal):
		p_energy_loss_keV[i] = v
	
	

def AT_Vavilov_energy_loss_distribution(p_energy_loss_keV, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_fDdD):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the energy loss
	Vavilov distribution acc. to CERN W5013
	No effective projectile charge is considered!
	@param[in]  	   n      				number of energy loss data
	@param[in]  	   energy_loss_keV      energy loss (array of size n)
	@param[in]  	   E_MeV_u      		energy of particle per nucleon
	@param[in]  	   particle_no  		particle index
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um
	@param[out]     fDdD (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_energy_loss_keV]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_fDdD is passed correctly:
	if len(p_fDdD) != len(p_energy_loss_keV):
		out_array_auto_init = "\nWarning: OUT array parameter p_fDdD was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_fDdD.clear()
		p_fDdD += [0]*len(p_energy_loss_keV)
	
	# Array sizes variables initialization:
	p_n = len(p_energy_loss_keV)
	p_n__internal = p_n
	p_energy_loss_keV__internal = p_energy_loss_keV
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_fDdD__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_fDdD):
		p_fDdD__internal[i] = v
	
	_libAT.lib.AT_Vavilov_energy_loss_distribution(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_energy_loss_keV__internal.encode() if type(p_energy_loss_keV__internal) is str else p_energy_loss_keV__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_fDdD__internal.encode() if type(p_fDdD__internal) is str else p_fDdD__internal
			)
	for i,v in enumerate(p_fDdD__internal):
		p_fDdD[i] = v
	
	

def AT_Gauss_PDF(p_lambda_gauss, p_density):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes Gauss probability density function (for compatibility)
	@param[in]  n             array size
	@param[in]  lambda_gauss  Gauss lambda (array of size n)
	@param[out] density       resulting density (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_lambda_gauss]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_density is passed correctly:
	if len(p_density) != len(p_lambda_gauss):
		out_array_auto_init = "\nWarning: OUT array parameter p_density was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_density.clear()
		p_density += [0]*len(p_lambda_gauss)
	
	# Array sizes variables initialization:
	p_n = len(p_lambda_gauss)
	p_n__internal = p_n
	p_lambda_gauss__internal = p_lambda_gauss
	p_density__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_density):
		p_density__internal[i] = v
	
	_libAT.lib.AT_Gauss_PDF(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_lambda_gauss__internal.encode() if type(p_lambda_gauss__internal) is str else p_lambda_gauss__internal
			,p_density__internal.encode() if type(p_density__internal) is str else p_density__internal
			)
	for i,v in enumerate(p_density__internal):
		p_density[i] = v
	
	

def AT_Gauss_IDF(p_rnd, p_lambda_gauss):
	"""
	Wrapping function generated for C language function documented as follows:
	Compute Gauss inverse distribution function (for compatibility)
	@param[in]  n             array size
	@param[in]  rnd           random number from uniform distribution between 0 and 1 (array of size n)
	@param[out] lambda_gauss  resulting Gauss lambda (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_rnd]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_lambda_gauss is passed correctly:
	if len(p_lambda_gauss) != len(p_rnd):
		out_array_auto_init = "\nWarning: OUT array parameter p_lambda_gauss was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_lambda_gauss.clear()
		p_lambda_gauss += [0]*len(p_rnd)
	
	# Array sizes variables initialization:
	p_n = len(p_rnd)
	p_n__internal = p_n
	p_rnd__internal = p_rnd
	p_lambda_gauss__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_lambda_gauss):
		p_lambda_gauss__internal[i] = v
	
	_libAT.lib.AT_Gauss_IDF(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_rnd__internal.encode() if type(p_rnd__internal) is str else p_rnd__internal
			,p_lambda_gauss__internal.encode() if type(p_lambda_gauss__internal) is str else p_lambda_gauss__internal
			)
	for i,v in enumerate(p_lambda_gauss__internal):
		p_lambda_gauss[i] = v
	
	

def AT_energy_loss_from_lambda_gauss_multi(p_lambda_gauss, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_energy_loss_keV):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the energy loss from the lambda parameter of the
	Gauss distribution for compatibility with CERN W5013
	No effective projectile charge is considered!
	@param[in]  	   n      				number of energy loss data
	@param[in]  	   lambda_gauss      Gauss lambda (array of size n)
	@param[in]  	   E_MeV_u      		energy of particle per nucleon (array of size n)
	@param[in]  	   particle_no  		particle index (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um (array of size n)
	@param[out]     energy_loss_keV (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_lambda_gauss,p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_lambda_gauss)
	for in_array_argument in [p_lambda_gauss,p_E_MeV_u,p_particle_no,p_slab_thickness_um]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_energy_loss_keV is passed correctly:
	if len(p_energy_loss_keV) != len(p_slab_thickness_um):
		out_array_auto_init = "\nWarning: OUT array parameter p_energy_loss_keV was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_energy_loss_keV.clear()
		p_energy_loss_keV += [0]*len(p_slab_thickness_um)
	
	# Array sizes variables initialization:
	p_n = len(p_lambda_gauss)
	p_n__internal = p_n
	p_lambda_gauss__internal = p_lambda_gauss
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_energy_loss_keV__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_energy_loss_keV):
		p_energy_loss_keV__internal[i] = v
	
	_libAT.lib.AT_energy_loss_from_lambda_gauss_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_lambda_gauss__internal.encode() if type(p_lambda_gauss__internal) is str else p_lambda_gauss__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_energy_loss_keV__internal.encode() if type(p_energy_loss_keV__internal) is str else p_energy_loss_keV__internal
			)
	for i,v in enumerate(p_energy_loss_keV__internal):
		p_energy_loss_keV[i] = v
	
	

def AT_Gauss_energy_loss_distribution(p_energy_loss_keV, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_fDdD):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the energy loss
	Gauss distribution
	@param[in]  	   n      				number of energy loss data
	@param[in]  	   energy_loss_keV      energy loss (array of size n)
	@param[in]  	   E_MeV_u      		energy of particle per nucleon
	@param[in]  	   particle_no  		particle index
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um
	@param[out]     fDdD (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_energy_loss_keV]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_fDdD is passed correctly:
	if len(p_fDdD) != len(p_energy_loss_keV):
		out_array_auto_init = "\nWarning: OUT array parameter p_fDdD was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_fDdD.clear()
		p_fDdD += [0]*len(p_energy_loss_keV)
	
	# Array sizes variables initialization:
	p_n = len(p_energy_loss_keV)
	p_n__internal = p_n
	p_energy_loss_keV__internal = p_energy_loss_keV
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_fDdD__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_fDdD):
		p_fDdD__internal[i] = v
	
	_libAT.lib.AT_Gauss_energy_loss_distribution(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_energy_loss_keV__internal.encode() if type(p_energy_loss_keV__internal) is str else p_energy_loss_keV__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_fDdD__internal.encode() if type(p_fDdD__internal) is str else p_fDdD__internal
			)
	for i,v in enumerate(p_fDdD__internal):
		p_fDdD[i] = v
	
	

def AT_Gauss_Mode():
	ret = _libAT.lib.AT_Gauss_Mode()
	return ret
	

def AT_Gauss_Mean():
	ret = _libAT.lib.AT_Gauss_Mean()
	return ret
	

def AT_Gauss_FWHM():
	ret = _libAT.lib.AT_Gauss_FWHM()
	return ret
	

def AT_energy_loss_distribution(p_energy_loss_keV, p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um, p_fDdD):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the energy loss distribution
	Uses Landau, Vavilov or Gauss depending on
	kappa parameter
	No effective projectile charge is considered!
	@param[in]  	   n      				number of energy loss data
	@param[in]  	   energy_loss_keV      energy loss (array of size n)
	@param[in]  	   E_MeV_u      		energy of particle per nucleon
	@param[in]  	   particle_no  		particle index
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  		material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um
	@param[out]     fDdD (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_energy_loss_keV]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_fDdD is passed correctly:
	if len(p_fDdD) != len(p_energy_loss_keV):
		out_array_auto_init = "\nWarning: OUT array parameter p_fDdD was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_fDdD.clear()
		p_fDdD += [0]*len(p_energy_loss_keV)
	
	# Array sizes variables initialization:
	p_n = len(p_energy_loss_keV)
	p_n__internal = p_n
	p_energy_loss_keV__internal = p_energy_loss_keV
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	p_fDdD__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_fDdD):
		p_fDdD__internal[i] = v
	
	_libAT.lib.AT_energy_loss_distribution(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_energy_loss_keV__internal.encode() if type(p_energy_loss_keV__internal) is str else p_energy_loss_keV__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			,p_fDdD__internal.encode() if type(p_fDdD__internal) is str else p_fDdD__internal
			)
	for i,v in enumerate(p_fDdD__internal):
		p_fDdD[i] = v
	
	

def AT_energy_loss_mode(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the most probable energy loss
	Uses Landau, Vavilov or Gauss depending on
	kappa parameter
	No effective projectile charge is considered!
	@param[in]  	   E_MeV_u      energy of particle per nucleon
	@param[in]  	   particle_no  particle index
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um
	@return     result
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_energy_loss_mode(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_energy_loss_FWHM(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_um):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the width of the energy loss distribution
	Uses Landau, Vavilov or Gauss depending on
	kappa parameter
	No effective projectile charge is considered!
	@param[in]  	   E_MeV_u      energy of particle per nucleon
	@param[in]  	   particle_no  particle index
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_um	slab thickness in um
	@return     result
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_um__internal = p_slab_thickness_um
	ret = _libAT.lib.AT_energy_loss_FWHM(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_um__internal.encode() if type(p_slab_thickness_um__internal) is str else p_slab_thickness_um__internal
			)
	return ret
	

def AT_dose_Bortfeld_Gy_single(p_z_cm, p_fluence_cm2, p_E_MeV, p_sigma_E_MeV, p_material_no, p_eps):
	"""
	Wrapping function generated for C language function documented as follows:
	@brief Proton analytical models of dose, LET and RBE
	Computes dose at given depth for proton beams according to analytical model of T. Bortfeld
	Bortfeld, 1997, An analytical approximation of the Bragg curve for therapeutic
	proton beams, Med. Phys. 24(12), 2024ff.
	@param[in] z_cm            depth in medium [cm]
	@param[in] fluence_cm2     proton fluence [1/cm2]
	@param[in] E_MeV           initial kinetic energy of proton beam [MeV]
	@param[in] sigma_E_MeV     kinetic energy spread (standard deviation) [MeV]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in] material_no     material code number
	@see          AT_DataMaterial.h for definition
	@param[in] eps             fraction of primary fluence contributing to the tail of energy spectrum
	if negative a default value of 0.03 is assumed
	@return                    dose at given depth [Gy]
	"""
	p_z_cm__internal = p_z_cm
	p_fluence_cm2__internal = p_fluence_cm2
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_material_no__internal = p_material_no
	p_eps__internal = p_eps
	ret = _libAT.lib.AT_dose_Bortfeld_Gy_single(p_z_cm__internal.encode() if type(p_z_cm__internal) is str else p_z_cm__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_eps__internal.encode() if type(p_eps__internal) is str else p_eps__internal
			)
	return ret
	

def AT_dose_Bortfeld_Gy_multi(p_z_cm, p_fluence_cm2, p_E_MeV, p_sigma_E_MeV, p_material_no, p_eps, p_dose_Gy):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes dose at given depth for proton beams according to analytical model of T. Bortfeld
	Bortfeld, 1997, An analytical approximation of the Bragg curve for therapeutic
	proton beams, Med. Phys. 24(12), 2024ff.
	@param[in]  n               number of depth steps
	@param[in]  z_cm            depths in medium [cm] (array of size n)
	@param[in]  fluence_cm2     proton fluence [1/cm2]
	@param[in]  E_MeV           initial kinetic energy of proton beam [MeV]
	@param[in]  sigma_E_MeV     kinetic energy spread (standard deviation) [MeV]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in]  material_no     material code number
	@see          AT_DataMaterial.h for definition
	@param[in]  eps             fraction of primary fluence contributing to the tail of energy spectrum
	if negative a default value of 0.03 is assumed
	@param[out] dose_Gy         doses at given depth [Gy] (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_z_cm]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_dose_Gy is passed correctly:
	if len(p_dose_Gy) != len(p_z_cm):
		out_array_auto_init = "\nWarning: OUT array parameter p_dose_Gy was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_dose_Gy.clear()
		p_dose_Gy += [0]*len(p_z_cm)
	
	# Array sizes variables initialization:
	p_n = len(p_z_cm)
	p_n__internal = p_n
	p_z_cm__internal = p_z_cm
	p_fluence_cm2__internal = p_fluence_cm2
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_material_no__internal = p_material_no
	p_eps__internal = p_eps
	p_dose_Gy__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_dose_Gy):
		p_dose_Gy__internal[i] = v
	
	_libAT.lib.AT_dose_Bortfeld_Gy_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_z_cm__internal.encode() if type(p_z_cm__internal) is str else p_z_cm__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_eps__internal.encode() if type(p_eps__internal) is str else p_eps__internal
			,p_dose_Gy__internal.encode() if type(p_dose_Gy__internal) is str else p_dose_Gy__internal
			)
	for i,v in enumerate(p_dose_Gy__internal):
		p_dose_Gy[i] = v
	
	

def AT_LET_t_Wilkens_keV_um_single(p_z_cm, p_E_MeV, p_sigma_E_MeV, p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes track averaged LET according to Wilkens model
	@param[in] z_cm            depth in medium [cm]
	@param[in] E_MeV           initial kinetic energy of proton beam [MeV]
	@param[in] sigma_E_MeV     kinetic energy spread (standard deviation) [MeV]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in] material_no     material code number
	@see          AT_DataMaterial.h for definition
	@return                    track averaged LET at given depth [keV/um]
	"""
	p_z_cm__internal = p_z_cm
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_LET_t_Wilkens_keV_um_single(p_z_cm__internal.encode() if type(p_z_cm__internal) is str else p_z_cm__internal
			,p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_LET_t_Wilkens_keV_um_multi(p_z_cm, p_E_MeV, p_sigma_E_MeV, p_material_no, p_LET_keV_um):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes track averaged LET according to Wilkens model
	@param[in]  n               number of depth steps
	@param[in]  z_cm            depths in medium [cm] (array of size n)
	@param[in]  E_MeV           initial kinetic energy of proton beam [MeV]
	@param[in]  sigma_E_MeV     kinetic energy spread (standard deviation) [MeV]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in]  material_no     material code number
	@see          AT_DataMaterial.h for definition
	@param[out] LET_keV_um      track averaged LET at given depth [keV/um] (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_z_cm]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_LET_keV_um is passed correctly:
	if len(p_LET_keV_um) != len(p_z_cm):
		out_array_auto_init = "\nWarning: OUT array parameter p_LET_keV_um was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_LET_keV_um.clear()
		p_LET_keV_um += [0]*len(p_z_cm)
	
	# Array sizes variables initialization:
	p_n = len(p_z_cm)
	p_n__internal = p_n
	p_z_cm__internal = p_z_cm
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_material_no__internal = p_material_no
	p_LET_keV_um__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_LET_keV_um):
		p_LET_keV_um__internal[i] = v
	
	_libAT.lib.AT_LET_t_Wilkens_keV_um_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_z_cm__internal.encode() if type(p_z_cm__internal) is str else p_z_cm__internal
			,p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_LET_keV_um__internal.encode() if type(p_LET_keV_um__internal) is str else p_LET_keV_um__internal
			)
	for i,v in enumerate(p_LET_keV_um__internal):
		p_LET_keV_um[i] = v
	
	

def AT_LET_d_Wilkens_keV_um_single(p_z_cm, p_E_MeV, p_sigma_E_MeV, p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes dose averaged LET according to Wilkens model
	@param[in] z_cm            depth in medium [cm]
	@param[in] E_MeV           initial kinetic energy of proton beam [MeV]
	@param[in] sigma_E_MeV     kinetic energy spread (standard deviation) [MeV]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in] material_no     material code number
	@see          AT_DataMaterial.h for definition
	@return                    track averaged LET at given depth [keV/um]
	"""
	p_z_cm__internal = p_z_cm
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_LET_d_Wilkens_keV_um_single(p_z_cm__internal.encode() if type(p_z_cm__internal) is str else p_z_cm__internal
			,p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_LET_d_Wilkens_keV_um_multi(p_z_cm, p_E_MeV, p_sigma_E_MeV, p_material_no, p_LET_keV_um):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes dose averaged LET according to Wilkens model
	@param[in]  n               number of depth steps
	@param[in]  z_cm            depths in medium [cm] (array of size n)
	@param[in]  E_MeV           initial kinetic energy of proton beam [MeV]
	@param[in]  sigma_E_MeV     kinetic energy spread (standard deviation) [MeV]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in]  material_no     material code number
	@see          AT_DataMaterial.h for definition
	@param[out] LET_keV_um      track averaged LET at given depth [keV/um] (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_z_cm]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_LET_keV_um is passed correctly:
	if len(p_LET_keV_um) != len(p_z_cm):
		out_array_auto_init = "\nWarning: OUT array parameter p_LET_keV_um was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_LET_keV_um.clear()
		p_LET_keV_um += [0]*len(p_z_cm)
	
	# Array sizes variables initialization:
	p_n = len(p_z_cm)
	p_n__internal = p_n
	p_z_cm__internal = p_z_cm
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_material_no__internal = p_material_no
	p_LET_keV_um__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_LET_keV_um):
		p_LET_keV_um__internal[i] = v
	
	_libAT.lib.AT_LET_d_Wilkens_keV_um_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_z_cm__internal.encode() if type(p_z_cm__internal) is str else p_z_cm__internal
			,p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_LET_keV_um__internal.encode() if type(p_LET_keV_um__internal) is str else p_LET_keV_um__internal
			)
	for i,v in enumerate(p_LET_keV_um__internal):
		p_LET_keV_um[i] = v
	
	

def AT_proton_RBE_single(p_z_cm, p_entrance_dose_Gy, p_E_MeV, p_sigma_E_MeV, p_eps, p_ref_alpha_beta_ratio, p_rbe_model_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes proton RBE according to one of several analytical models
	@param[in] z_cm              depth in medium [cm]
	@param[in] entrance_dose_Gy  entrance dose [Gy]
	@param[in] E_MeV             initial kinetic energy of proton beam [MeV]
	@param[in] sigma_E_MeV       kinetic energy spread (standard deviation) [MeV]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in] eps              fraction of primary fluence contributing to the tail of energy spectrum
	if negative a default value of 0.03 is assumed
	@param[in] ref_alpha_beta_ratio   ratio of alpha to beta (parameters in linear-quadratic model) for reference radiation
	@param[in] rbe_model_no   TODO
	@return                    proton RBE
	"""
	p_z_cm__internal = p_z_cm
	p_entrance_dose_Gy__internal = p_entrance_dose_Gy
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_eps__internal = p_eps
	p_ref_alpha_beta_ratio__internal = p_ref_alpha_beta_ratio
	p_rbe_model_no__internal = p_rbe_model_no
	ret = _libAT.lib.AT_proton_RBE_single(p_z_cm__internal.encode() if type(p_z_cm__internal) is str else p_z_cm__internal
			,p_entrance_dose_Gy__internal.encode() if type(p_entrance_dose_Gy__internal) is str else p_entrance_dose_Gy__internal
			,p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_eps__internal.encode() if type(p_eps__internal) is str else p_eps__internal
			,p_ref_alpha_beta_ratio__internal.encode() if type(p_ref_alpha_beta_ratio__internal) is str else p_ref_alpha_beta_ratio__internal
			,p_rbe_model_no__internal.encode() if type(p_rbe_model_no__internal) is str else p_rbe_model_no__internal
			)
	return ret
	

def AT_proton_RBE_multi(p_z_cm, p_entrance_dose_Gy, p_E_MeV, p_sigma_E_MeV, p_eps, p_ref_alpha_beta_ratio, p_rbe_model_no, p_rbe):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes proton RBE according to one of several analytical models
	@param[in]  n                 number of depth steps
	@param[in]  z_cm              depth in medium [cm] (array of size n)
	@param[in]  entrance_dose_Gy  entrance dose [Gy]
	@param[in]  E_MeV             initial kinetic energy of proton beam [MeV]
	@param[in]  sigma_E_MeV       kinetic energy spread (standard deviation) [MeV]
	if negative a default value of 0.01 * E_MeV is assumed
	@param[in]  eps               fraction of primary fluence contributing to the tail of energy spectrum
	if negative a default value of 0.03 is assumed
	@param[in]  ref_alpha_beta_ratio   ratio of alpha to beta (parameters in linear-quadratic model) for reference radiation
	@param[in]  rbe_model_no   TODO
	@param[out] rbe             proton RBE (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_z_cm]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_rbe is passed correctly:
	if len(p_rbe) != len(p_z_cm):
		out_array_auto_init = "\nWarning: OUT array parameter p_rbe was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_rbe.clear()
		p_rbe += [0]*len(p_z_cm)
	
	# Array sizes variables initialization:
	p_n = len(p_z_cm)
	p_n__internal = p_n
	p_z_cm__internal = p_z_cm
	p_entrance_dose_Gy__internal = p_entrance_dose_Gy
	p_E_MeV__internal = p_E_MeV
	p_sigma_E_MeV__internal = p_sigma_E_MeV
	p_eps__internal = p_eps
	p_ref_alpha_beta_ratio__internal = p_ref_alpha_beta_ratio
	p_rbe_model_no__internal = p_rbe_model_no
	p_rbe__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_rbe):
		p_rbe__internal[i] = v
	
	_libAT.lib.AT_proton_RBE_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_z_cm__internal.encode() if type(p_z_cm__internal) is str else p_z_cm__internal
			,p_entrance_dose_Gy__internal.encode() if type(p_entrance_dose_Gy__internal) is str else p_entrance_dose_Gy__internal
			,p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_sigma_E_MeV__internal.encode() if type(p_sigma_E_MeV__internal) is str else p_sigma_E_MeV__internal
			,p_eps__internal.encode() if type(p_eps__internal) is str else p_eps__internal
			,p_ref_alpha_beta_ratio__internal.encode() if type(p_ref_alpha_beta_ratio__internal) is str else p_ref_alpha_beta_ratio__internal
			,p_rbe_model_no__internal.encode() if type(p_rbe_model_no__internal) is str else p_rbe_model_no__internal
			,p_rbe__internal.encode() if type(p_rbe__internal) is str else p_rbe__internal
			)
	for i,v in enumerate(p_rbe__internal):
		p_rbe[i] = v
	
	

def AT_material_name_from_number(p_material_no, p_material_name):
	"""
	Wrapping function generated for C language function documented as follows:
	Get material name
	@param[in]  material_no
	@param[out] material_name
	"""
	if not isinstance(p_material_name, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_material_name) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_material_name.clear()
		p_material_name += ['']
	
	p_material_no__internal = p_material_no
	arg_keepalive = [ffi.new("char[]", 1)]
	p_material_name__internal = ffi.new("char* []", arg_keepalive)
	_libAT.lib.AT_material_name_from_number(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_material_name__internal[0].encode() if type(p_material_name__internal[0]) is str else p_material_name__internal[0]
			)
	for i,v in enumerate(p_material_name__internal):
		p_material_name[i] = ffi.string(v).decode()
	
	

def AT_material_number_from_name(p_material_name):
	"""
	Wrapping function generated for C language function documented as follows:
	Get material number
	@param[in] material_name
	@return    material number
	"""
	p_material_name__internal = p_material_name
	ret = _libAT.lib.AT_material_number_from_name(p_material_name__internal.encode() if type(p_material_name__internal) is str else p_material_name__internal
			)
	return ret
	

def AT_density_g_cm3_from_material_no(p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Get material density [g/cm3] for single material with number material_no
	@param[in] material_no
	@return    material density [g/cm3]
	"""
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_density_g_cm3_from_material_no(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_I_eV_from_material_no(p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Get mean ionization potential in eV for single material with number material_no
	@param[in] material_no
	@return    mean ionization potential [eV]
	"""
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_I_eV_from_material_no(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_alpha_g_cm2_MeV_from_material_no(p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Get fit parameter for power-law representation of stp.power/range/E-dependence for single material with number material_no
	@param[in] material_no
	@return    fit parameter for power-law representation of stp.power/range/E-dependence
	"""
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_alpha_g_cm2_MeV_from_material_no(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_p_MeV_from_material_no(p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Get fit parameter for power-law representation of stp.power/range/E-dependence for single material with number material_no
	@param[in] material_no
	@return    fit parameter for power-law representation of stp.power/range/E-dependence
	"""
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_p_MeV_from_material_no(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_m_g_cm2_from_material_no(p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Get fit parameter for the linear representation of fluence changes due to nuclear interactions based on data from Janni for single material with number material_no
	@param[in] material_no
	@return    fit parameter for the linear representation of fluence changes due to nuclear interactions based on data from Janni
	"""
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_m_g_cm2_from_material_no(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_average_A_from_material_no(p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Get average mass number for single material with number material_no
	@param[in] material_no
	@return    average mass number
	"""
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_average_A_from_material_no(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_average_Z_from_material_no(p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Get average atomic number for single material with number material_no
	@param[in] material_no
	@return    average atomic number
	"""
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_average_Z_from_material_no(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_phase_from_material_no(p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Get material phase
	@param[in] material_no
	@return    material phase index (enumerator)
	"""
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_phase_from_material_no(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_get_material_data(p_material_no, p_density_g_cm3, p_I_eV, p_alpha_g_cm2_MeV, p_p_MeV, p_m_g_cm2, p_average_A, p_average_Z):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns material data for single material
	@param[in]  material_no           index number of material
	@param[out] density_g_cm3         physical density [g/cm3]
	electron_density = number_of_electron_per_molecule * avogadro_constant / molar_mass * 1m3 * density
	@param[out] I_eV                  mean ionization potential [eV]
	@param[out] alpha_g_cm2_MeV       fit parameter for power-law representation of stopping-power (Bortfeld, 1997)
	@see  Bortfeld, T. (1997), An analytical approximation of the Bragg curve for therapeutic proton beams, Med. Phys. 24, 2024ff.
	Here, however, we use the mass stopping power. The correct dimension is g/(cm^2 * MeV^p)
	@param[out] p_MeV                 fit parameter for power-law representation of stopping-power (Bortfeld, 1997)
	@see  Bortfeld, T. (1997), An analytical approximation of the Bragg curve for therapeutic proton beams, Med. Phys. 24, 2024ff.\n
	p is actually dimensionless, it should be nevertheless indicated, that the energy must be given in MeV
	@param[out] m_g_cm2               fit parameter for the linear representation of fluence changes due to nuclear interactions based on data from Janni 1982  (Bortfeld, 1997)
	@see  Bortfeld, T. (1997), An analytical approximation of the Bragg curve for therapeutic proton beams, Med. Phys. 24, 2024ff.
	@param[out] average_A             average mass number
	let f_i be fraction by weight of the constituent element with atomic number Z_i and atomic weight A_i\n
	let us define average_Z/A = sum_i f_i Z_i / A_i \n
	then we have: average_A = average_Z / (average_Z/A) \n
	for water (H20) we have: average_Z/A = (2/18) * (1/1) + (16/18)*(8/16) = 0.5555 \n
	average_A = 7.22 / 0.555 = 13
	@param[out] average_Z             average atomic number
	let f_i be fraction by weight of the constituent element with atomic number Z_i and atomic weight A_i\n
	average_Z = sum_i f_i Z_i \n
	for water (H20) we have: average_Z = (2/18)*1 + (16/18)*8 = 7.22\n
	@see Tabata, T. (1972) Generalized semiempirical equations for the extrapolated range of electrons, Nucl. Instr and Meth. 103, 85-91.
	"""
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_density_g_cm3)
	for in_array_argument in [p_density_g_cm3,p_I_eV,p_alpha_g_cm2_MeV,p_p_MeV,p_m_g_cm2,p_average_A,p_average_Z]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_density_g_cm3)
	for in_array_argument in [p_density_g_cm3,p_I_eV,p_alpha_g_cm2_MeV,p_p_MeV,p_m_g_cm2,p_average_A,p_average_Z]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_density_g_cm3, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_I_eV, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_alpha_g_cm2_MeV, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_p_MeV, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_m_g_cm2, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_average_A, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_average_Z, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_density_g_cm3) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_density_g_cm3.clear()
		p_density_g_cm3 += [0]
	
	if len(p_I_eV) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_I_eV.clear()
		p_I_eV += [0]
	
	if len(p_alpha_g_cm2_MeV) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_alpha_g_cm2_MeV.clear()
		p_alpha_g_cm2_MeV += [0]
	
	if len(p_p_MeV) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_p_MeV.clear()
		p_p_MeV += [0]
	
	if len(p_m_g_cm2) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_m_g_cm2.clear()
		p_m_g_cm2 += [0]
	
	if len(p_average_A) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_average_A.clear()
		p_average_A += [0]
	
	if len(p_average_Z) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_average_Z.clear()
		p_average_Z += [0]
	
	p_material_no__internal = p_material_no
	p_density_g_cm3__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_density_g_cm3):
		p_density_g_cm3__internal[i] = v
	
	p_I_eV__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_I_eV):
		p_I_eV__internal[i] = v
	
	p_alpha_g_cm2_MeV__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_alpha_g_cm2_MeV):
		p_alpha_g_cm2_MeV__internal[i] = v
	
	p_p_MeV__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_p_MeV):
		p_p_MeV__internal[i] = v
	
	p_m_g_cm2__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_m_g_cm2):
		p_m_g_cm2__internal[i] = v
	
	p_average_A__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_average_A):
		p_average_A__internal[i] = v
	
	p_average_Z__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_average_Z):
		p_average_Z__internal[i] = v
	
	_libAT.lib.AT_get_material_data(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_density_g_cm3__internal.encode() if type(p_density_g_cm3__internal) is str else p_density_g_cm3__internal
			,p_I_eV__internal.encode() if type(p_I_eV__internal) is str else p_I_eV__internal
			,p_alpha_g_cm2_MeV__internal.encode() if type(p_alpha_g_cm2_MeV__internal) is str else p_alpha_g_cm2_MeV__internal
			,p_p_MeV__internal.encode() if type(p_p_MeV__internal) is str else p_p_MeV__internal
			,p_m_g_cm2__internal.encode() if type(p_m_g_cm2__internal) is str else p_m_g_cm2__internal
			,p_average_A__internal.encode() if type(p_average_A__internal) is str else p_average_A__internal
			,p_average_Z__internal.encode() if type(p_average_Z__internal) is str else p_average_Z__internal
			)
	for i,v in enumerate(p_density_g_cm3__internal):
		p_density_g_cm3[i] = v
	
	for i,v in enumerate(p_I_eV__internal):
		p_I_eV[i] = v
	
	for i,v in enumerate(p_alpha_g_cm2_MeV__internal):
		p_alpha_g_cm2_MeV[i] = v
	
	for i,v in enumerate(p_p_MeV__internal):
		p_p_MeV[i] = v
	
	for i,v in enumerate(p_m_g_cm2__internal):
		p_m_g_cm2[i] = v
	
	for i,v in enumerate(p_average_A__internal):
		p_average_A[i] = v
	
	for i,v in enumerate(p_average_Z__internal):
		p_average_Z[i] = v
	
	

def AT_get_materials_data(p_material_no, p_density_g_cm3, p_I_eV, p_alpha_g_cm2_MeV, p_p_MeV, p_m_g_cm2, p_average_A, p_average_Z):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns material data for list of materials
	@param[in]   number_of_materials  numbers of materials the routine is called for
	@param[in]   material_no          material indices (array of size number_of_materials)
	@param[out]  density_g_cm3        material density in g/cm3 (array of size number_of_materials)
	@param[out]  I_eV                 mean ionization potential in eV (array of size number_of_materials)
	@param[out]  alpha_g_cm2_MeV      fit parameter for power-law representation of stp.power/range/E-dependence (array of size number_of_materials)
	@param[out]  p_MeV                fit parameter for power-law representation of stp.power/range/E-dependence (array of size number_of_materials)
	@param[out]  m_g_cm2              fit parameter for the linear representation of fluence changes due to nuclear interactions based on data from Janni 1982 (array of size number_of_materials)
	@param[out]  average_A            average mass number (array of size number_of_materials)
	@param[out]  average_Z            average atomic number (array of size number_of_materials)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_material_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_density_g_cm3 is passed correctly:
	if len(p_density_g_cm3) != len(p_material_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_density_g_cm3 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_density_g_cm3.clear()
		p_density_g_cm3 += [0]*len(p_material_no)
	
	# Procedure to check if OUT array p_I_eV is passed correctly:
	if len(p_I_eV) != len(p_material_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_I_eV was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_I_eV.clear()
		p_I_eV += [0]*len(p_material_no)
	
	# Procedure to check if OUT array p_alpha_g_cm2_MeV is passed correctly:
	if len(p_alpha_g_cm2_MeV) != len(p_material_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_alpha_g_cm2_MeV was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_alpha_g_cm2_MeV.clear()
		p_alpha_g_cm2_MeV += [0]*len(p_material_no)
	
	# Procedure to check if OUT array p_p_MeV is passed correctly:
	if len(p_p_MeV) != len(p_material_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_p_MeV was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_p_MeV.clear()
		p_p_MeV += [0]*len(p_material_no)
	
	# Procedure to check if OUT array p_m_g_cm2 is passed correctly:
	if len(p_m_g_cm2) != len(p_material_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_m_g_cm2 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_m_g_cm2.clear()
		p_m_g_cm2 += [0]*len(p_material_no)
	
	# Procedure to check if OUT array p_average_A is passed correctly:
	if len(p_average_A) != len(p_material_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_average_A was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_average_A.clear()
		p_average_A += [0]*len(p_material_no)
	
	# Procedure to check if OUT array p_average_Z is passed correctly:
	if len(p_average_Z) != len(p_material_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_average_Z was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_average_Z.clear()
		p_average_Z += [0]*len(p_material_no)
	
	# Array sizes variables initialization:
	p_number_of_materials = len(p_material_no)
	p_number_of_materials__internal = p_number_of_materials
	p_material_no__internal = p_material_no
	p_density_g_cm3__internal = ffi.new("double[]", p_number_of_materials)
	for i,v in enumerate(p_density_g_cm3):
		p_density_g_cm3__internal[i] = v
	
	p_I_eV__internal = ffi.new("double[]", p_number_of_materials)
	for i,v in enumerate(p_I_eV):
		p_I_eV__internal[i] = v
	
	p_alpha_g_cm2_MeV__internal = ffi.new("double[]", p_number_of_materials)
	for i,v in enumerate(p_alpha_g_cm2_MeV):
		p_alpha_g_cm2_MeV__internal[i] = v
	
	p_p_MeV__internal = ffi.new("double[]", p_number_of_materials)
	for i,v in enumerate(p_p_MeV):
		p_p_MeV__internal[i] = v
	
	p_m_g_cm2__internal = ffi.new("double[]", p_number_of_materials)
	for i,v in enumerate(p_m_g_cm2):
		p_m_g_cm2__internal[i] = v
	
	p_average_A__internal = ffi.new("double[]", p_number_of_materials)
	for i,v in enumerate(p_average_A):
		p_average_A__internal[i] = v
	
	p_average_Z__internal = ffi.new("double[]", p_number_of_materials)
	for i,v in enumerate(p_average_Z):
		p_average_Z__internal[i] = v
	
	_libAT.lib.AT_get_materials_data(p_number_of_materials__internal.encode() if type(p_number_of_materials__internal) is str else p_number_of_materials__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_density_g_cm3__internal.encode() if type(p_density_g_cm3__internal) is str else p_density_g_cm3__internal
			,p_I_eV__internal.encode() if type(p_I_eV__internal) is str else p_I_eV__internal
			,p_alpha_g_cm2_MeV__internal.encode() if type(p_alpha_g_cm2_MeV__internal) is str else p_alpha_g_cm2_MeV__internal
			,p_p_MeV__internal.encode() if type(p_p_MeV__internal) is str else p_p_MeV__internal
			,p_m_g_cm2__internal.encode() if type(p_m_g_cm2__internal) is str else p_m_g_cm2__internal
			,p_average_A__internal.encode() if type(p_average_A__internal) is str else p_average_A__internal
			,p_average_Z__internal.encode() if type(p_average_Z__internal) is str else p_average_Z__internal
			)
	for i,v in enumerate(p_density_g_cm3__internal):
		p_density_g_cm3[i] = v
	
	for i,v in enumerate(p_I_eV__internal):
		p_I_eV[i] = v
	
	for i,v in enumerate(p_alpha_g_cm2_MeV__internal):
		p_alpha_g_cm2_MeV[i] = v
	
	for i,v in enumerate(p_p_MeV__internal):
		p_p_MeV[i] = v
	
	for i,v in enumerate(p_m_g_cm2__internal):
		p_m_g_cm2[i] = v
	
	for i,v in enumerate(p_average_A__internal):
		p_average_A[i] = v
	
	for i,v in enumerate(p_average_Z__internal):
		p_average_Z[i] = v
	
	

def AT_electron_density_m3_from_material_no_single(p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Get electron density [1/m3] for single material with number material_no
	@param[in] material_no
	@return    electron density [1/m3]
	"""
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_electron_density_m3_from_material_no_single(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_electron_density_m3_from_material_no_multi(p_material_no, p_electron_density_m3):
	"""
	Wrapping function generated for C language function documented as follows:
	Get electron density [1/m3] for materials
	@param[in]     n                    number of materials
	@param[in]     material_no          material indices (array of size n)
	@param[out]    electron_density_m3  electron densities per m3 (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_material_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_electron_density_m3 is passed correctly:
	if len(p_electron_density_m3) != len(p_material_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_electron_density_m3 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_electron_density_m3.clear()
		p_electron_density_m3 += [0]*len(p_material_no)
	
	# Array sizes variables initialization:
	p_n = len(p_material_no)
	p_n__internal = p_n
	p_material_no__internal = p_material_no
	p_electron_density_m3__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_electron_density_m3):
		p_electron_density_m3__internal[i] = v
	
	_libAT.lib.AT_electron_density_m3_from_material_no_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_electron_density_m3__internal.encode() if type(p_electron_density_m3__internal) is str else p_electron_density_m3__internal
			)
	for i,v in enumerate(p_electron_density_m3__internal):
		p_electron_density_m3[i] = v
	
	

def AT_plasma_energy_J_from_material_no(p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns material's plasma energy needed for Sternheimer
	computation of density effect in stopping power
	@param[in]  material_no  material number
	"""
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_plasma_energy_J_from_material_no(p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_electron_density_m3_single(p_density_g_cm3, p_average_Z, p_average_A):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the electron density from average A and Z
	@param[in] density_g_cm3      physical density (in g/cm3) of material
	@param[in] average_Z          average atomic number of material
	@param[in] average_A          mass number of material
	@return                       electron density in 1/m3
	"""
	p_density_g_cm3__internal = p_density_g_cm3
	p_average_Z__internal = p_average_Z
	p_average_A__internal = p_average_A
	ret = _libAT.lib.AT_electron_density_m3_single(p_density_g_cm3__internal.encode() if type(p_density_g_cm3__internal) is str else p_density_g_cm3__internal
			,p_average_Z__internal.encode() if type(p_average_Z__internal) is str else p_average_Z__internal
			,p_average_A__internal.encode() if type(p_average_A__internal) is str else p_average_A__internal
			)
	return ret
	

def AT_electron_density_m3_multi(p_density_g_cm3, p_average_Z, p_average_A, p_electron_density_m3):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns electron density from average A and Z
	@param[in]   n                    size of arrays
	@param[in]   density_g_cm3        material density in g/cm3 (array of size n)
	@param[in]   average_A            average mass number (array of size n)
	@param[in]   average_Z            average atomic number (array of size n)
	@param[out]  electron_density_m3  electron density in 1/m3 (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_density_g_cm3,p_average_Z,p_average_A]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_density_g_cm3)
	for in_array_argument in [p_density_g_cm3,p_average_Z,p_average_A]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_electron_density_m3 is passed correctly:
	if len(p_electron_density_m3) != len(p_average_A):
		out_array_auto_init = "\nWarning: OUT array parameter p_electron_density_m3 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_electron_density_m3.clear()
		p_electron_density_m3 += [0]*len(p_average_A)
	
	# Array sizes variables initialization:
	p_n = len(p_density_g_cm3)
	p_n__internal = p_n
	p_density_g_cm3__internal = p_density_g_cm3
	p_average_Z__internal = p_average_Z
	p_average_A__internal = p_average_A
	p_electron_density_m3__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_electron_density_m3):
		p_electron_density_m3__internal[i] = v
	
	_libAT.lib.AT_electron_density_m3_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_density_g_cm3__internal.encode() if type(p_density_g_cm3__internal) is str else p_density_g_cm3__internal
			,p_average_Z__internal.encode() if type(p_average_Z__internal) is str else p_average_Z__internal
			,p_average_A__internal.encode() if type(p_average_A__internal) is str else p_average_A__internal
			,p_electron_density_m3__internal.encode() if type(p_electron_density_m3__internal) is str else p_electron_density_m3__internal
			)
	for i,v in enumerate(p_electron_density_m3__internal):
		p_electron_density_m3[i] = v
	
	

def AT_plasma_energy_J_single(p_electron_density_m3):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns plasma energy needed for Sternheimer
	computation of density effect in stopping power
	@param[in]  electron_density_m3  electron density in 1/m3
	"""
	p_electron_density_m3__internal = p_electron_density_m3
	ret = _libAT.lib.AT_plasma_energy_J_single(p_electron_density_m3__internal.encode() if type(p_electron_density_m3__internal) is str else p_electron_density_m3__internal
			)
	return ret
	

def AT_electron_density_m3_from_composition(p_density_g_cm3, p_Z, p_A, p_weight_fraction, p_electron_density_m3):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the electron density for a given material composition
	@param[in]  n                     number of constituents in material
	@param[in]  density_g_cm3         physical density (in g per cm3) of material
	@param[in]  Z                     atomic numbers of constituents (array of size n)
	@param[in]  A                     mass numbers of constituents (array of size n)
	@param[in]  weight_fraction       relative fractions of weight of constituents (array of size n)
	@param[out] electron_density_m3   electron density per m3
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_Z,p_A,p_weight_fraction]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_Z)
	for in_array_argument in [p_Z,p_A,p_weight_fraction]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_electron_density_m3, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_electron_density_m3) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_electron_density_m3.clear()
		p_electron_density_m3 += [0]
	
	# Array sizes variables initialization:
	p_n = len(p_Z)
	p_n__internal = p_n
	p_density_g_cm3__internal = p_density_g_cm3
	p_Z__internal = p_Z
	p_A__internal = p_A
	p_weight_fraction__internal = p_weight_fraction
	p_electron_density_m3__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_electron_density_m3):
		p_electron_density_m3__internal[i] = v
	
	_libAT.lib.AT_electron_density_m3_from_composition(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_density_g_cm3__internal.encode() if type(p_density_g_cm3__internal) is str else p_density_g_cm3__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			,p_weight_fraction__internal.encode() if type(p_weight_fraction__internal) is str else p_weight_fraction__internal
			,p_electron_density_m3__internal.encode() if type(p_electron_density_m3__internal) is str else p_electron_density_m3__internal
			)
	for i,v in enumerate(p_electron_density_m3__internal):
		p_electron_density_m3[i] = v
	
	

def AT_average_A_from_composition(p_A, p_weight_fraction, p_average_A):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the average mass number A for a given material composition
	It is a weighted average where weights are relative fraction of weight of constituents
	A_av = \sum fi Ai
	Note that this is different from a value used by Tabata in delta electron range modelling
	@param[in]  n                     number of constituents in material
	@param[in]  A                     mass numbers of constituents (array of size n)
	@param[in]  weight_fraction       relative fractions of weight of constituents (array of size n)
	@param[out] average_A             average A
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_A,p_weight_fraction]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_A)
	for in_array_argument in [p_A,p_weight_fraction]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_average_A, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_average_A) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_average_A.clear()
		p_average_A += [0]
	
	# Array sizes variables initialization:
	p_n = len(p_A)
	p_n__internal = p_n
	p_A__internal = p_A
	p_weight_fraction__internal = p_weight_fraction
	p_average_A__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_average_A):
		p_average_A__internal[i] = v
	
	_libAT.lib.AT_average_A_from_composition(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			,p_weight_fraction__internal.encode() if type(p_weight_fraction__internal) is str else p_weight_fraction__internal
			,p_average_A__internal.encode() if type(p_average_A__internal) is str else p_average_A__internal
			)
	for i,v in enumerate(p_average_A__internal):
		p_average_A[i] = v
	
	

def AT_average_Z_from_composition(p_Z, p_weight_fraction, p_average_Z):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the average atomic Z number for a given material composition.
	It is a weighted average where weights are relative fraction of weight of constituents
	Z_av = \sum fi Zi
	@param[in]  n                     number of constituents in material
	@param[in]  Z                     atomic numbers of constituents (array of size n)
	@param[in]  weight_fraction       relative fractions of weight of constituents (array of size n)
	@param[out] average_Z             average Z
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_Z,p_weight_fraction]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_Z)
	for in_array_argument in [p_Z,p_weight_fraction]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_average_Z, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_average_Z) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_average_Z.clear()
		p_average_Z += [0]
	
	# Array sizes variables initialization:
	p_n = len(p_Z)
	p_n__internal = p_n
	p_Z__internal = p_Z
	p_weight_fraction__internal = p_weight_fraction
	p_average_Z__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_average_Z):
		p_average_Z__internal[i] = v
	
	_libAT.lib.AT_average_Z_from_composition(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_weight_fraction__internal.encode() if type(p_weight_fraction__internal) is str else p_weight_fraction__internal
			,p_average_Z__internal.encode() if type(p_average_Z__internal) is str else p_average_Z__internal
			)
	for i,v in enumerate(p_average_Z__internal):
		p_average_Z[i] = v
	
	

def AT_effective_Z_from_composition(p_Z, p_weight_fraction, p_electron_densities_cm3, p_exponent, p_effective_Z):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the effective atomic number for a given material composition
	@param[in]  n                     	number of constituents in material
	@param[in]  Z                     	atomic numbers of constituents (array of size n)
	@param[in]  weight_fraction       	relative fractions of weight of constituents (array of size n)
	@param[in]  electron_densities_cm3   if not zero, weight fractions will additionally include electron densities per volume (array of size n)
	@param[in]  exponent              	exponent for additivity rule reflecting the photon energy regime (usually 3.5 at ~ 100 kV)
	@param[out] effective_Z           	effective Z
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_Z,p_weight_fraction,p_electron_densities_cm3]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_Z)
	for in_array_argument in [p_Z,p_weight_fraction,p_electron_densities_cm3]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_effective_Z, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_effective_Z) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_effective_Z.clear()
		p_effective_Z += [0]
	
	# Array sizes variables initialization:
	p_n = len(p_Z)
	p_n__internal = p_n
	p_Z__internal = p_Z
	p_weight_fraction__internal = p_weight_fraction
	p_electron_densities_cm3__internal = p_electron_densities_cm3
	p_exponent__internal = p_exponent
	p_effective_Z__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_effective_Z):
		p_effective_Z__internal[i] = v
	
	_libAT.lib.AT_effective_Z_from_composition(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_weight_fraction__internal.encode() if type(p_weight_fraction__internal) is str else p_weight_fraction__internal
			,p_electron_densities_cm3__internal.encode() if type(p_electron_densities_cm3__internal) is str else p_electron_densities_cm3__internal
			,p_exponent__internal.encode() if type(p_exponent__internal) is str else p_exponent__internal
			,p_effective_Z__internal.encode() if type(p_effective_Z__internal) is str else p_effective_Z__internal
			)
	for i,v in enumerate(p_effective_Z__internal):
		p_effective_Z[i] = v
	
	

def AT_I_eV_from_composition(p_Z, p_A, p_weight_fraction, p_I_eV):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the I value for a given material composition
	@param[in]  n                     number of constituents in material
	@param[in]  Z                     atomic numbers of constituents (array of size n)
	@param[in]  A                     mass numbers of constituents (array of size n)
	@param[in]  weight_fraction       relative fractions of weight of constituents (array of size n)
	@param[out] I_eV                  I value in eV
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_Z,p_A,p_weight_fraction]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_Z)
	for in_array_argument in [p_Z,p_A,p_weight_fraction]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_I_eV, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_I_eV) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_I_eV.clear()
		p_I_eV += [0]
	
	# Array sizes variables initialization:
	p_n = len(p_Z)
	p_n__internal = p_n
	p_Z__internal = p_Z
	p_A__internal = p_A
	p_weight_fraction__internal = p_weight_fraction
	p_I_eV__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_I_eV):
		p_I_eV__internal[i] = v
	
	_libAT.lib.AT_I_eV_from_composition(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			,p_weight_fraction__internal.encode() if type(p_weight_fraction__internal) is str else p_weight_fraction__internal
			,p_I_eV__internal.encode() if type(p_I_eV__internal) is str else p_I_eV__internal
			)
	for i,v in enumerate(p_I_eV__internal):
		p_I_eV[i] = v
	
	

def AT_particle_no_from_Z_and_A_single(p_Z, p_A):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in]  Z            atomic number
	@param[in]  A            mass number
	@return particle_no
	"""
	p_Z__internal = p_Z
	p_A__internal = p_A
	ret = _libAT.lib.AT_particle_no_from_Z_and_A_single(p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			)
	return ret
	

def AT_particle_no_from_Z_and_A(p_Z, p_A, p_particle_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns particle index number from given A and Z
	@param[in]  n            array sizes
	@param[in]  Z            atomic numbers (array of size n)
	@param[in]  A            mass number (array of size n)
	@param[out] particle_no  corresponding particle index numbers (array of size n)
	@return status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_Z,p_A]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_Z)
	for in_array_argument in [p_Z,p_A]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_particle_no is passed correctly:
	if len(p_particle_no) != len(p_A):
		out_array_auto_init = "\nWarning: OUT array parameter p_particle_no was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_particle_no.clear()
		p_particle_no += [0]*len(p_A)
	
	# Array sizes variables initialization:
	p_n = len(p_Z)
	p_n__internal = p_n
	p_Z__internal = p_Z
	p_A__internal = p_A
	p_particle_no__internal = ffi.new("long[]", p_n)
	for i,v in enumerate(p_particle_no):
		p_particle_no__internal[i] = v
	
	ret = _libAT.lib.AT_particle_no_from_Z_and_A(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			)
	for i,v in enumerate(p_particle_no__internal):
		p_particle_no[i] = v
	
	return ret
	

def AT_A_from_particle_no_single(p_particle_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates mass number A for particle with given code number
	@param[in] particle_no
	@return A
	"""
	p_particle_no__internal = p_particle_no
	ret = _libAT.lib.AT_A_from_particle_no_single(p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			)
	return ret
	

def AT_A_from_particle_no(p_particle_no, p_A):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns mass number for given particle number
	@param[in]  n                length of arrays
	@param[in]  particle_no      particle index number (array of size n)
	@param[out] A                mass number (array of size n)
	@return     return code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_A is passed correctly:
	if len(p_A) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_A was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_A.clear()
		p_A += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_particle_no)
	p_n__internal = p_n
	p_particle_no__internal = p_particle_no
	p_A__internal = ffi.new("long[]", p_n)
	for i,v in enumerate(p_A):
		p_A__internal[i] = v
	
	ret = _libAT.lib.AT_A_from_particle_no(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			)
	for i,v in enumerate(p_A__internal):
		p_A[i] = v
	
	return ret
	

def AT_atomic_weight_from_Z(p_Z, p_atomic_weight):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns atomic weight for given Z
	@param[in]  n                length of arrays
	@param[in]  Z                atomic number (array of size n)
	@param[out] atomic_weight    atomic weight (array of size n)
	@return     return code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_Z]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_atomic_weight is passed correctly:
	if len(p_atomic_weight) != len(p_Z):
		out_array_auto_init = "\nWarning: OUT array parameter p_atomic_weight was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_atomic_weight.clear()
		p_atomic_weight += [0]*len(p_Z)
	
	# Array sizes variables initialization:
	p_n = len(p_Z)
	p_n__internal = p_n
	p_Z__internal = p_Z
	p_atomic_weight__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_atomic_weight):
		p_atomic_weight__internal[i] = v
	
	ret = _libAT.lib.AT_atomic_weight_from_Z(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_atomic_weight__internal.encode() if type(p_atomic_weight__internal) is str else p_atomic_weight__internal
			)
	for i,v in enumerate(p_atomic_weight__internal):
		p_atomic_weight[i] = v
	
	return ret
	

def AT_Z_from_particle_no_single(p_particle_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates atomic number Z for particle with given code number
	@param[in] particle_no
	@return Z
	"""
	p_particle_no__internal = p_particle_no
	ret = _libAT.lib.AT_Z_from_particle_no_single(p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			)
	return ret
	

def AT_Z_from_particle_no(p_particle_no, p_Z):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns atomic number for given particle number
	@param[in]  n               length of arrays
	@param[in]  particle_no     particle index number (array of size n)
	@param[out] Z               atomic number (array of size n)
	@return     return code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_Z is passed correctly:
	if len(p_Z) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_Z was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_Z.clear()
		p_Z += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_particle_no)
	p_n__internal = p_n
	p_particle_no__internal = p_particle_no
	p_Z__internal = ffi.new("long[]", p_n)
	for i,v in enumerate(p_Z):
		p_Z__internal[i] = v
	
	ret = _libAT.lib.AT_Z_from_particle_no(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			)
	for i,v in enumerate(p_Z__internal):
		p_Z[i] = v
	
	return ret
	

def AT_atomic_weight_from_particle_no_single(p_particle_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates atomic weight for particle with given code number
	@param[in]  particle_no    particle index number
	@return     atomic_weight  atomic weight
	"""
	p_particle_no__internal = p_particle_no
	ret = _libAT.lib.AT_atomic_weight_from_particle_no_single(p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			)
	return ret
	

def AT_atomic_weight_from_particle_no(p_particle_no, p_atomic_weight):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates atomic weight for particle with given code number
	@param[in]  n              length of arrays
	@param[in]  particle_no    particle index number (array of size n)
	@param[out] atomic_weight  atomic weight (array of size n)
	@return                    status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_atomic_weight is passed correctly:
	if len(p_atomic_weight) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_atomic_weight was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_atomic_weight.clear()
		p_atomic_weight += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_particle_no)
	p_n__internal = p_n
	p_particle_no__internal = p_particle_no
	p_atomic_weight__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_atomic_weight):
		p_atomic_weight__internal[i] = v
	
	ret = _libAT.lib.AT_atomic_weight_from_particle_no(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_atomic_weight__internal.encode() if type(p_atomic_weight__internal) is str else p_atomic_weight__internal
			)
	for i,v in enumerate(p_atomic_weight__internal):
		p_atomic_weight[i] = v
	
	return ret
	

def AT_I_eV_from_particle_no(p_particle_no, p_I_eV):
	"""
	Wrapping function generated for C language function documented as follows:
	Return I value for given elements
	@param[in]  n              number of elements
	@param[in]  particle_no    particle index number (array of size n)
	@param[out] I_eV           I value (array of size n)
	@return                    status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_I_eV is passed correctly:
	if len(p_I_eV) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_I_eV was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_I_eV.clear()
		p_I_eV += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_particle_no)
	p_n__internal = p_n
	p_particle_no__internal = p_particle_no
	p_I_eV__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_I_eV):
		p_I_eV__internal[i] = v
	
	ret = _libAT.lib.AT_I_eV_from_particle_no(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_I_eV__internal.encode() if type(p_I_eV__internal) is str else p_I_eV__internal
			)
	for i,v in enumerate(p_I_eV__internal):
		p_I_eV[i] = v
	
	return ret
	

def AT_nuclear_spin_from_particle_no_multi(p_particle_no, p_I):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns nuclear spin from particle no
	@param[in]  n              number of elements
	@param[in]  particle_no    particle index number (array of size n)
	@param[out] I              nuclear spin (array of size n)
	@return                    status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_I is passed correctly:
	if len(p_I) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_I was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_I.clear()
		p_I += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_particle_no)
	p_n__internal = p_n
	p_particle_no__internal = p_particle_no
	p_I__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_I):
		p_I__internal[i] = v
	
	ret = _libAT.lib.AT_nuclear_spin_from_particle_no_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_I__internal.encode() if type(p_I__internal) is str else p_I__internal
			)
	for i,v in enumerate(p_I__internal):
		p_I[i] = v
	
	return ret
	

def AT_nuclear_spin_from_particle_no_single(p_particle_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns nuclear spin from particle no
	@param[in]  particle_no    particle index number (array of size n)
	@return     nuclear spin
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Array sizes variables initialization:
	p_n = len(p_particle_no)
	p_particle_no__internal = p_particle_no
	ret = _libAT.lib.AT_nuclear_spin_from_particle_no_single(p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			)
	return ret
	

def AT_nuclear_spin_from_Z_and_A(p_Z, p_A):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns nuclear spin from Z and A
	@param[in]  Z              atomic number
	@param[in]  A              mass number
	@return     nuclear spin
	"""
	p_Z__internal = p_Z
	p_A__internal = p_A
	ret = _libAT.lib.AT_nuclear_spin_from_Z_and_A(p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			)
	return ret
	

def AT_particle_name_from_particle_no_single(p_particle_no, p_particle_name):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns particle index name for given particle index number
	@param[in]  particle_no    particle index number
	@param[out] particle_name  corresponding particle name
	@return status
	"""
	if not isinstance(p_particle_name, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_particle_name) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_particle_name.clear()
		p_particle_name += ['']
	
	p_particle_no__internal = p_particle_no
	arg_keepalive = [ffi.new("char[]", 1)]
	p_particle_name__internal = ffi.new("char* []", arg_keepalive)
	ret = _libAT.lib.AT_particle_name_from_particle_no_single(p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_particle_name__internal[0].encode() if type(p_particle_name__internal[0]) is str else p_particle_name__internal[0]
			)
	for i,v in enumerate(p_particle_name__internal):
		p_particle_name[i] = ffi.string(v).decode()
	
	return ret
	

def AT_particle_no_from_particle_name_single(p_particle_name):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns particle index number for given particle name
	@param[in]  particle_name particle index name (array of size 6)
	@return corresponding particle number
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_particle_name]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	p_particle_name__internal = p_particle_name
	ret = _libAT.lib.AT_particle_no_from_particle_name_single(p_particle_name__internal.encode() if type(p_particle_name__internal) is str else p_particle_name__internal
			)
	return ret
	

def AT_particle_name_from_particle_no(p_particle_no, p_particle_name):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns particle index numbers for given particle names
	@param[in]  n             TODO
	@param[in]  particle_no   particle index numbers (array of size n)
	@param[out] particle_name corresponding particle names (array of size n)
	@return status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_particle_name is passed correctly:
	if len(p_particle_name) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_particle_name was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_particle_name.clear()
		p_particle_name += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_particle_no)
	p_n__internal = p_n
	p_particle_no__internal = p_particle_no
	arg_keepalive = [ffi.new("char[]", 1)]
	p_particle_name__internal = ffi.new("char* []", arg_keepalive)
	ret = _libAT.lib.AT_particle_name_from_particle_no(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_particle_name__internal[0].encode() if type(p_particle_name__internal[0]) is str else p_particle_name__internal[0]
			)
	for i,v in enumerate(p_particle_name__internal):
		p_particle_name[i] = ffi.string(v).decode()
	
	return ret
	

def AT_particle_no_from_particle_name(p_particle_name, p_particle_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns particle names for given particle numbers
	@param[in]  n              TODO
	@param[in]  particle_name  particle names (array of size n)
	@param[out] particle_no    type of the particles (array of size n)
	@return status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_particle_name]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_particle_no is passed correctly:
	if len(p_particle_no) != len(p_particle_name):
		out_array_auto_init = "\nWarning: OUT array parameter p_particle_no was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_particle_no.clear()
		p_particle_no += [0]*len(p_particle_name)
	
	# Array sizes variables initialization:
	p_n = len(p_particle_name)
	p_n__internal = p_n
	arg_keepalive = [ffi.new("char[]", x.encode() if type(x) is str else x) for x in p_particle_name]
	p_particle_name__internal = ffi.new("char* []", arg_keepalive)
	p_particle_no__internal = ffi.new("long[]", p_n)
	for i,v in enumerate(p_particle_no):
		p_particle_no__internal[i] = v
	
	ret = _libAT.lib.AT_particle_no_from_particle_name(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_particle_name__internal.encode() if type(p_particle_name__internal) is str else p_particle_name__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			)
	for i,v in enumerate(p_particle_no__internal):
		p_particle_no[i] = v
	
	return ret
	

def AT_Z_from_element_acronym_single(p_acronym):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns Z for given elemental symbol
	@param[in]  acronym        elemental symbols (array of size 6)
	@return corresponding Z
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	p_acronym__internal = p_acronym
	ret = _libAT.lib.AT_Z_from_element_acronym_single(p_acronym__internal.encode() if type(p_acronym__internal) is str else p_acronym__internal
			)
	return ret
	

def AT_Z_from_element_acronym(p_acronym, p_Z):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns Z for given elemental symbols
	@param[in]  n       number of elements
	@param[in]  acronym elemental symbols (array of size n)
	@param[out] Z       corresponding Z (array of size n)
	@return status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_Z is passed correctly:
	if len(p_Z) != len(p_acronym):
		out_array_auto_init = "\nWarning: OUT array parameter p_Z was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_Z.clear()
		p_Z += [0]*len(p_acronym)
	
	# Array sizes variables initialization:
	p_n = len(p_acronym)
	p_n__internal = p_n
	arg_keepalive = [ffi.new("char[]", x.encode() if type(x) is str else x) for x in p_acronym]
	p_acronym__internal = ffi.new("char* []", arg_keepalive)
	p_Z__internal = ffi.new("long[]", p_n)
	for i,v in enumerate(p_Z):
		p_Z__internal[i] = v
	
	ret = _libAT.lib.AT_Z_from_element_acronym(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_acronym__internal.encode() if type(p_acronym__internal) is str else p_acronym__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			)
	for i,v in enumerate(p_Z__internal):
		p_Z[i] = v
	
	return ret
	

def AT_element_acronym_from_Z_single(p_Z, p_acronym):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns elemental symbol for given Z
	@param[in]  Z      atomic number
	@param[out] acronym  corresponding elemental symbol (array of size 6)
	return status
	"""
	p_Z__internal = p_Z
	arg_keepalive = [ffi.new("char[]", 1)]
	p_acronym__internal = ffi.new("char* []", arg_keepalive)
	ret = _libAT.lib.AT_element_acronym_from_Z_single(p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_acronym__internal[0].encode() if type(p_acronym__internal[0]) is str else p_acronym__internal[0]
			)
	for i,v in enumerate(p_acronym__internal):
		p_acronym[i] = ffi.string(v).decode()
	
	return ret
	

def AT_element_acronym_from_Z(p_Z, p_acronym):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns elemental symbols for given Z
	@param[in]  n       number of elements
	@param[in]  Z       atomic numbers (array of size n)
	@param[out] acronym corresponding elemental symbols (array of size n)
	@return status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_Z]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_acronym is passed correctly:
	if len(p_acronym) != len(p_Z):
		out_array_auto_init = "\nWarning: OUT array parameter p_acronym was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_acronym.clear()
		p_acronym += [0]*len(p_Z)
	
	# Array sizes variables initialization:
	p_n = len(p_Z)
	p_n__internal = p_n
	p_Z__internal = p_Z
	ret = _libAT.lib.AT_element_acronym_from_Z(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_acronym__internal.encode() if type(p_acronym__internal) is str else p_acronym__internal
			)
	return ret
	

def AT_atomic_weight_from_element_acronym_single(p_acronym):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns atomic weight for given elemental symbol
	@param[in]  acronym   elemental symbols (array of size 6)
	@return corresponding atomic weight
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	p_acronym__internal = p_acronym
	ret = _libAT.lib.AT_atomic_weight_from_element_acronym_single(p_acronym__internal.encode() if type(p_acronym__internal) is str else p_acronym__internal
			)
	return ret
	

def AT_atomic_weight_from_element_acronym(p_acronym, p_atomic_weight):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns atomic weight for given elemental symbols
	@param[in]  n               number of elements in array
	@param[in]  acronym         elemental symbols (array of size n)
	@param[out] atomic_weight   corresponding A (array of size n)
	@return status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_atomic_weight is passed correctly:
	if len(p_atomic_weight) != len(p_acronym):
		out_array_auto_init = "\nWarning: OUT array parameter p_atomic_weight was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_atomic_weight.clear()
		p_atomic_weight += [0]*len(p_acronym)
	
	# Array sizes variables initialization:
	p_n = len(p_acronym)
	p_n__internal = p_n
	arg_keepalive = [ffi.new("char[]", x.encode() if type(x) is str else x) for x in p_acronym]
	p_acronym__internal = ffi.new("char* []", arg_keepalive)
	p_atomic_weight__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_atomic_weight):
		p_atomic_weight__internal[i] = v
	
	ret = _libAT.lib.AT_atomic_weight_from_element_acronym(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_acronym__internal.encode() if type(p_acronym__internal) is str else p_acronym__internal
			,p_atomic_weight__internal.encode() if type(p_atomic_weight__internal) is str else p_atomic_weight__internal
			)
	for i,v in enumerate(p_atomic_weight__internal):
		p_atomic_weight[i] = v
	
	return ret
	

def AT_density_g_cm3_from_element_acronym_single(p_acronym):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the elemental density in g/cm3 for given elemental symbol
	@param[in]  acronym   elemental symbols (array of size 6)
	@return elemental density in g/cm3
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	p_acronym__internal = p_acronym
	ret = _libAT.lib.AT_density_g_cm3_from_element_acronym_single(p_acronym__internal.encode() if type(p_acronym__internal) is str else p_acronym__internal
			)
	return ret
	

def AT_density_g_cm3_from_element_acronym(p_acronym, p_density):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the elemental densities in g/cm3 for given elemental symbols
	@param[in]  n        number of elements in array
	@param[in]  acronym  elemental symbols (array of size n)
	@param[out] density  corresponding elemental densities in g/cm3 (array of size n)
	@return status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_density is passed correctly:
	if len(p_density) != len(p_acronym):
		out_array_auto_init = "\nWarning: OUT array parameter p_density was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_density.clear()
		p_density += [0]*len(p_acronym)
	
	# Array sizes variables initialization:
	p_n = len(p_acronym)
	p_n__internal = p_n
	arg_keepalive = [ffi.new("char[]", x.encode() if type(x) is str else x) for x in p_acronym]
	p_acronym__internal = ffi.new("char* []", arg_keepalive)
	p_density__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_density):
		p_density__internal[i] = v
	
	ret = _libAT.lib.AT_density_g_cm3_from_element_acronym(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_acronym__internal.encode() if type(p_acronym__internal) is str else p_acronym__internal
			,p_density__internal.encode() if type(p_density__internal) is str else p_density__internal
			)
	for i,v in enumerate(p_density__internal):
		p_density[i] = v
	
	return ret
	

def AT_I_eV_from_element_acronym_single(p_acronym):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the I value in eV for given elemental symbol
	@param[in]  acronym  elemental symbol (array of size 6)
	@return corresponding I value in eV
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	p_acronym__internal = p_acronym
	ret = _libAT.lib.AT_I_eV_from_element_acronym_single(p_acronym__internal.encode() if type(p_acronym__internal) is str else p_acronym__internal
			)
	return ret
	

def AT_I_eV_from_element_acronym(p_acronym, p_I):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the I values in eV for given elemental symbol
	@param[in]  n        number of elements in array
	@param[in]  acronym  elemental symbols (array of size n)
	@param[out] I        corresponding I values in eV (array of size n)
	@return status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_I is passed correctly:
	if len(p_I) != len(p_acronym):
		out_array_auto_init = "\nWarning: OUT array parameter p_I was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_I.clear()
		p_I += [0]*len(p_acronym)
	
	# Array sizes variables initialization:
	p_n = len(p_acronym)
	p_n__internal = p_n
	arg_keepalive = [ffi.new("char[]", x.encode() if type(x) is str else x) for x in p_acronym]
	p_acronym__internal = ffi.new("char* []", arg_keepalive)
	p_I__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_I):
		p_I__internal[i] = v
	
	ret = _libAT.lib.AT_I_eV_from_element_acronym(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_acronym__internal.encode() if type(p_acronym__internal) is str else p_acronym__internal
			,p_I__internal.encode() if type(p_I__internal) is str else p_I__internal
			)
	for i,v in enumerate(p_I__internal):
		p_I[i] = v
	
	return ret
	

def AT_electron_density_cm3_from_element_acronym_single(p_acronym):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the electron density per cm3 for given elemental symbol
	@param[in]   acronym  elemental symbol (array of size 6)
	@return      corresponding electron density per cm3
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	p_acronym__internal = p_acronym
	ret = _libAT.lib.AT_electron_density_cm3_from_element_acronym_single(p_acronym__internal.encode() if type(p_acronym__internal) is str else p_acronym__internal
			)
	return ret
	

def AT_electron_density_cm3_from_element_acronym(p_acronym, p_electron_density):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the electron densities per cm3 for given elemental symbols
	@param[in]  n                       array length
	@param[in]  acronym                 elemental symbols (array of size n)
	@param[out] electron_density        corresponding electron densities per cm3 (array of size n)
	@return status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_electron_density is passed correctly:
	if len(p_electron_density) != len(p_acronym):
		out_array_auto_init = "\nWarning: OUT array parameter p_electron_density was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_electron_density.clear()
		p_electron_density += [0]*len(p_acronym)
	
	# Array sizes variables initialization:
	p_n = len(p_acronym)
	p_n__internal = p_n
	arg_keepalive = [ffi.new("char[]", x.encode() if type(x) is str else x) for x in p_acronym]
	p_acronym__internal = ffi.new("char* []", arg_keepalive)
	p_electron_density__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_electron_density):
		p_electron_density__internal[i] = v
	
	ret = _libAT.lib.AT_electron_density_cm3_from_element_acronym(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_acronym__internal.encode() if type(p_acronym__internal) is str else p_acronym__internal
			,p_electron_density__internal.encode() if type(p_electron_density__internal) is str else p_electron_density__internal
			)
	for i,v in enumerate(p_electron_density__internal):
		p_electron_density[i] = v
	
	return ret
	

def AT_Gamma_name_from_number(p_Gamma_no, p_Gamma_name):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns name of the gamma response model from model number
	@param[in]  Gamma_no    gamma response model number
	@param[out] Gamma_name  string containing gamma response model name
	"""
	if not isinstance(p_Gamma_name, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_Gamma_name) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_Gamma_name.clear()
		p_Gamma_name += ['']
	
	p_Gamma_no__internal = p_Gamma_no
	arg_keepalive = [ffi.new("char[]", 1)]
	p_Gamma_name__internal = ffi.new("char* []", arg_keepalive)
	_libAT.lib.AT_Gamma_name_from_number(p_Gamma_no__internal.encode() if type(p_Gamma_no__internal) is str else p_Gamma_no__internal
			,p_Gamma_name__internal[0].encode() if type(p_Gamma_name__internal[0]) is str else p_Gamma_name__internal[0]
			)
	for i,v in enumerate(p_Gamma_name__internal):
		p_Gamma_name[i] = ffi.string(v).decode()
	
	

def AT_Gamma_number_of_parameters(p_Gamma_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns number of parameters of the gamma response model from model number
	@param[in]   Gamma_no   gamma response model number
	return                  number of GR parameters
	"""
	p_Gamma_no__internal = p_Gamma_no
	ret = _libAT.lib.AT_Gamma_number_of_parameters(p_Gamma_no__internal.encode() if type(p_Gamma_no__internal) is str else p_Gamma_no__internal
			)
	return ret
	

def AT_gamma_response(p_d_Gy, p_gamma_model, p_gamma_parameter, p_lethal_event_mode, p_S):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns a system (detector or cells) response for given doses
	according to the chosen gamma response model
	@param[in]  number_of_doses  number of doses given in vector d_Gy
	@param[in]  d_Gy             doses in Gy (array of size number_of_doses)
	@param[in]  gamma_model      gamma response model index
	@param[in]  gamma_parameter  vector holding necessary parameters for the chose gamma response model (array of size 9)
	@param[in]  lethal_event_mode  if true computation is done in lethal event mode
	@param[out] S         gamma responses (array of size number_of_doses)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_d_Gy,p_gamma_parameter]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_S is passed correctly:
	if len(p_S) != len(p_d_Gy):
		out_array_auto_init = "\nWarning: OUT array parameter p_S was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_S.clear()
		p_S += [0]*len(p_d_Gy)
	
	# Array sizes variables initialization:
	p_number_of_doses = len(p_d_Gy)
	p_number_of_doses__internal = p_number_of_doses
	p_d_Gy__internal = p_d_Gy
	p_gamma_model__internal = p_gamma_model
	p_gamma_parameter__internal = p_gamma_parameter
	p_lethal_event_mode__internal = p_lethal_event_mode
	p_S__internal = ffi.new("double[]", p_number_of_doses)
	for i,v in enumerate(p_S):
		p_S__internal[i] = v
	
	_libAT.lib.AT_gamma_response(p_number_of_doses__internal.encode() if type(p_number_of_doses__internal) is str else p_number_of_doses__internal
			,p_d_Gy__internal.encode() if type(p_d_Gy__internal) is str else p_d_Gy__internal
			,p_gamma_model__internal.encode() if type(p_gamma_model__internal) is str else p_gamma_model__internal
			,p_gamma_parameter__internal.encode() if type(p_gamma_parameter__internal) is str else p_gamma_parameter__internal
			,p_lethal_event_mode__internal.encode() if type(p_lethal_event_mode__internal) is str else p_lethal_event_mode__internal
			,p_S__internal.encode() if type(p_S__internal) is str else p_S__internal
			)
	for i,v in enumerate(p_S__internal):
		p_S[i] = v
	
	

def AT_get_gamma_response_for_average_dose(p_dose_Gy_bin_position, p_dose_Gy_bin_width, p_dose_bin_frequency, p_gamma_model, p_gamma_parameter, p_lethal_events_mode):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the detector / cell gamma response for dose distribution
	@param[in]  number_of_bins            number of bins in the dose histogram
	@param[in]  dose_Gy_bin_position      midpoint doses for histogram in Gy (array of size number_of_bins)
	@param[in]  dose_Gy_bin_width         bin widths for histogram in Gy (array of size number_of_bins)
	@param[in]  dose_bin_frequency        dose frequencies for histogram (array of size number_of_bins)
	@param[in]  gamma_model               gamma response model index
	@param[in]  gamma_parameter           vector holding necessary parameters for the chose gamma response model (array of size 9)
	@param[in]  lethal_events_mode        if true computation is done in lethal event mode
	@return     response
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_dose_Gy_bin_position,p_dose_Gy_bin_width,p_dose_bin_frequency,p_gamma_parameter]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_bins
	declared_in_arr_param_size__number_of_bins = len(p_dose_Gy_bin_position)
	for in_array_argument in [p_dose_Gy_bin_position,p_dose_Gy_bin_width,p_dose_bin_frequency]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_bins:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_bins = len(p_dose_Gy_bin_position)
	p_number_of_bins__internal = p_number_of_bins
	p_dose_Gy_bin_position__internal = p_dose_Gy_bin_position
	p_dose_Gy_bin_width__internal = p_dose_Gy_bin_width
	p_dose_bin_frequency__internal = p_dose_bin_frequency
	p_gamma_model__internal = p_gamma_model
	p_gamma_parameter__internal = p_gamma_parameter
	p_lethal_events_mode__internal = p_lethal_events_mode
	ret = _libAT.lib.AT_get_gamma_response_for_average_dose(p_number_of_bins__internal.encode() if type(p_number_of_bins__internal) is str else p_number_of_bins__internal
			,p_dose_Gy_bin_position__internal.encode() if type(p_dose_Gy_bin_position__internal) is str else p_dose_Gy_bin_position__internal
			,p_dose_Gy_bin_width__internal.encode() if type(p_dose_Gy_bin_width__internal) is str else p_dose_Gy_bin_width__internal
			,p_dose_bin_frequency__internal.encode() if type(p_dose_bin_frequency__internal) is str else p_dose_bin_frequency__internal
			,p_gamma_model__internal.encode() if type(p_gamma_model__internal) is str else p_gamma_model__internal
			,p_gamma_parameter__internal.encode() if type(p_gamma_parameter__internal) is str else p_gamma_parameter__internal
			,p_lethal_events_mode__internal.encode() if type(p_lethal_events_mode__internal) is str else p_lethal_events_mode__internal
			)
	return ret
	

def AT_get_response_distribution_from_dose_distribution(p_dose_Gy_bin_position, p_dose_bin_frequency, p_gamma_model, p_gamma_parameter, p_lethal_events_mode, p_response_bin_frequency):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the detector / cell gamma response for dose distribution
	@param[in]  number_of_bins            number of bins in the dose histogram
	@param[in]  dose_Gy_bin_position      midpoint doses for histogram in Gy (array of size number_of_bins)
	@param[in]  dose_bin_frequency        dose frequencies for histogram (array of size number_of_bins)
	@param[in]  gamma_model               gamma response model index
	@param[in]  gamma_parameter           vector holding necessary parameters for the chose gamma response model (array of size 9)
	@param[in]  lethal_events_mode        if true computation is done in lethal event mode
	@param[out] response_bin_frequency    resulting response frequencies (array of size number_of_bins)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_dose_Gy_bin_position,p_dose_bin_frequency,p_gamma_parameter]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_bins
	declared_in_arr_param_size__number_of_bins = len(p_dose_Gy_bin_position)
	for in_array_argument in [p_dose_Gy_bin_position,p_dose_bin_frequency]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_bins:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_response_bin_frequency is passed correctly:
	if len(p_response_bin_frequency) != len(p_dose_bin_frequency):
		out_array_auto_init = "\nWarning: OUT array parameter p_response_bin_frequency was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_response_bin_frequency.clear()
		p_response_bin_frequency += [0]*len(p_dose_bin_frequency)
	
	# Array sizes variables initialization:
	p_number_of_bins = len(p_dose_Gy_bin_position)
	p_number_of_bins__internal = p_number_of_bins
	p_dose_Gy_bin_position__internal = p_dose_Gy_bin_position
	p_dose_bin_frequency__internal = p_dose_bin_frequency
	p_gamma_model__internal = p_gamma_model
	p_gamma_parameter__internal = p_gamma_parameter
	p_lethal_events_mode__internal = p_lethal_events_mode
	p_response_bin_frequency__internal = ffi.new("double[]", p_number_of_bins)
	for i,v in enumerate(p_response_bin_frequency):
		p_response_bin_frequency__internal[i] = v
	
	_libAT.lib.AT_get_response_distribution_from_dose_distribution(p_number_of_bins__internal.encode() if type(p_number_of_bins__internal) is str else p_number_of_bins__internal
			,p_dose_Gy_bin_position__internal.encode() if type(p_dose_Gy_bin_position__internal) is str else p_dose_Gy_bin_position__internal
			,p_dose_bin_frequency__internal.encode() if type(p_dose_bin_frequency__internal) is str else p_dose_bin_frequency__internal
			,p_gamma_model__internal.encode() if type(p_gamma_model__internal) is str else p_gamma_model__internal
			,p_gamma_parameter__internal.encode() if type(p_gamma_parameter__internal) is str else p_gamma_parameter__internal
			,p_lethal_events_mode__internal.encode() if type(p_lethal_events_mode__internal) is str else p_lethal_events_mode__internal
			,p_response_bin_frequency__internal.encode() if type(p_response_bin_frequency__internal) is str else p_response_bin_frequency__internal
			)
	for i,v in enumerate(p_response_bin_frequency__internal):
		p_response_bin_frequency[i] = v
	
	

def AT_get_ion_response_from_response_distribution(p_dose_Gy_bin_width, p_dose_bin_frequency, p_ion_response_bin_frequency):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the ion response from an ion response distribution
	@param[in]  number_of_bins                number of bins in the dose histogram
	@param[in]  dose_Gy_bin_width             bin widths for histogram in Gy (array of size number_of_bins)
	@param[in]  dose_bin_frequency            dose frequencies for histogram (array of size number_of_bins)
	@param[in]  ion_response_bin_frequency    ion response frequencies (array of size number_of_bins)
	@return     response
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_dose_Gy_bin_width,p_dose_bin_frequency,p_ion_response_bin_frequency]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_bins
	declared_in_arr_param_size__number_of_bins = len(p_dose_Gy_bin_width)
	for in_array_argument in [p_dose_Gy_bin_width,p_dose_bin_frequency,p_ion_response_bin_frequency]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_bins:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_bins = len(p_dose_Gy_bin_width)
	p_number_of_bins__internal = p_number_of_bins
	p_dose_Gy_bin_width__internal = p_dose_Gy_bin_width
	p_dose_bin_frequency__internal = p_dose_bin_frequency
	p_ion_response_bin_frequency__internal = p_ion_response_bin_frequency
	ret = _libAT.lib.AT_get_ion_response_from_response_distribution(p_number_of_bins__internal.encode() if type(p_number_of_bins__internal) is str else p_number_of_bins__internal
			,p_dose_Gy_bin_width__internal.encode() if type(p_dose_Gy_bin_width__internal) is str else p_dose_Gy_bin_width__internal
			,p_dose_bin_frequency__internal.encode() if type(p_dose_bin_frequency__internal) is str else p_dose_bin_frequency__internal
			,p_ion_response_bin_frequency__internal.encode() if type(p_ion_response_bin_frequency__internal) is str else p_ion_response_bin_frequency__internal
			)
	return ret
	

def AT_get_ion_response_from_dose_distribution(p_dose_Gy_bin_position, p_dose_Gy_bin_width, p_dose_bin_frequency, p_gamma_model, p_gamma_parameter, p_lethal_events_mode):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns ion response for dose distribution
	@param[in]  number_of_bins            number of bins in the dose histogram
	@param[in]  dose_Gy_bin_position      midpoint doses for histogram in Gy (array of size number_of_bins)
	@param[in]  dose_bin_frequency        dose frequencies for histogram (array of size number_of_bins)
	@param[in]  gamma_model               gamma response model index
	@param[in]  gamma_parameter           vector holding necessary parameters for the chose gamma response model (array of size 9)
	@param[in]  lethal_events_mode        if true computation is done in lethal event mode
	@param[in]  dose_Gy_bin_width        TODO
	@return     resulting ion response
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_dose_Gy_bin_position,p_dose_bin_frequency,p_gamma_parameter]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_bins
	declared_in_arr_param_size__number_of_bins = len(p_dose_Gy_bin_position)
	for in_array_argument in [p_dose_Gy_bin_position,p_dose_bin_frequency]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_bins:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_bins = len(p_dose_Gy_bin_position)
	p_number_of_bins__internal = p_number_of_bins
	p_dose_Gy_bin_position__internal = p_dose_Gy_bin_position
	p_dose_Gy_bin_width__internal = p_dose_Gy_bin_width
	p_dose_bin_frequency__internal = p_dose_bin_frequency
	p_gamma_model__internal = p_gamma_model
	p_gamma_parameter__internal = p_gamma_parameter
	p_lethal_events_mode__internal = p_lethal_events_mode
	ret = _libAT.lib.AT_get_ion_response_from_dose_distribution(p_number_of_bins__internal.encode() if type(p_number_of_bins__internal) is str else p_number_of_bins__internal
			,p_dose_Gy_bin_position__internal.encode() if type(p_dose_Gy_bin_position__internal) is str else p_dose_Gy_bin_position__internal
			,p_dose_Gy_bin_width__internal.encode() if type(p_dose_Gy_bin_width__internal) is str else p_dose_Gy_bin_width__internal
			,p_dose_bin_frequency__internal.encode() if type(p_dose_bin_frequency__internal) is str else p_dose_bin_frequency__internal
			,p_gamma_model__internal.encode() if type(p_gamma_model__internal) is str else p_gamma_model__internal
			,p_gamma_parameter__internal.encode() if type(p_gamma_parameter__internal) is str else p_gamma_parameter__internal
			,p_lethal_events_mode__internal.encode() if type(p_lethal_events_mode__internal) is str else p_lethal_events_mode__internal
			)
	return ret
	

def AT_get_ion_efficiency_from_dose_distribution(p_dose_Gy_bin_position, p_dose_Gy_bin_width, p_dose_bin_frequency, p_gamma_model, p_gamma_parameter, p_lethal_events_mode):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns relative efficiency for dose distribution
	@param[in]  number_of_bins            number of bins in the dose histogram
	@param[in]  dose_Gy_bin_position      midpoint doses for histogram in Gy (array of size number_of_bins)
	@param[in]  dose_bin_frequency        dose frequencies for histogram (array of size number_of_bins)
	@param[in]  gamma_model               gamma response model index
	@param[in]  gamma_parameter           vector holding necessary parameters for the chose gamma response model (array of size 9)
	@param[in]  lethal_events_mode        if true computation is done in lethal event mode
	@param[in]  dose_Gy_bin_width        TODO
	@return     relative efficiency
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_dose_Gy_bin_position,p_dose_bin_frequency,p_gamma_parameter]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_bins
	declared_in_arr_param_size__number_of_bins = len(p_dose_Gy_bin_position)
	for in_array_argument in [p_dose_Gy_bin_position,p_dose_bin_frequency]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_bins:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_bins = len(p_dose_Gy_bin_position)
	p_number_of_bins__internal = p_number_of_bins
	p_dose_Gy_bin_position__internal = p_dose_Gy_bin_position
	p_dose_Gy_bin_width__internal = p_dose_Gy_bin_width
	p_dose_bin_frequency__internal = p_dose_bin_frequency
	p_gamma_model__internal = p_gamma_model
	p_gamma_parameter__internal = p_gamma_parameter
	p_lethal_events_mode__internal = p_lethal_events_mode
	ret = _libAT.lib.AT_get_ion_efficiency_from_dose_distribution(p_number_of_bins__internal.encode() if type(p_number_of_bins__internal) is str else p_number_of_bins__internal
			,p_dose_Gy_bin_position__internal.encode() if type(p_dose_Gy_bin_position__internal) is str else p_dose_Gy_bin_position__internal
			,p_dose_Gy_bin_width__internal.encode() if type(p_dose_Gy_bin_width__internal) is str else p_dose_Gy_bin_width__internal
			,p_dose_bin_frequency__internal.encode() if type(p_dose_bin_frequency__internal) is str else p_dose_bin_frequency__internal
			,p_gamma_model__internal.encode() if type(p_gamma_model__internal) is str else p_gamma_model__internal
			,p_gamma_parameter__internal.encode() if type(p_gamma_parameter__internal) is str else p_gamma_parameter__internal
			,p_lethal_events_mode__internal.encode() if type(p_lethal_events_mode__internal) is str else p_lethal_events_mode__internal
			)
	return ret
	

def AT_get_ion_efficiency_from_response_distribution(p_dose_Gy_bin_position, p_dose_Gy_bin_width, p_dose_bin_frequency, p_ion_response_bin_frequency, p_gamma_model, p_gamma_parameter, p_lethal_events_mode):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns relative efficiency from ion response distribution
	@param[in]  number_of_bins            number of bins in the dose histogram
	@param[in]  dose_Gy_bin_position      midpoint doses for histogram in Gy (array of size number_of_bins)
	@param[in]  dose_bin_frequency        dose frequencies for histogram (array of size number_of_bins)
	@param[in]  ion_response_bin_frequency    ion response frequencies (array of size number_of_bins)
	@param[in]  gamma_model               gamma response model index
	@param[in]  gamma_parameter           vector holding necessary parameters for the chose gamma response model (array of size 9)
	@param[in]  lethal_events_mode        if true computation is done in lethal event mode
	@param[in]  dose_Gy_bin_width        TODO
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_dose_Gy_bin_position,p_dose_bin_frequency,p_ion_response_bin_frequency,p_gamma_parameter]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_bins
	declared_in_arr_param_size__number_of_bins = len(p_dose_Gy_bin_position)
	for in_array_argument in [p_dose_Gy_bin_position,p_dose_bin_frequency,p_ion_response_bin_frequency]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_bins:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_bins = len(p_dose_Gy_bin_position)
	p_number_of_bins__internal = p_number_of_bins
	p_dose_Gy_bin_position__internal = p_dose_Gy_bin_position
	p_dose_Gy_bin_width__internal = p_dose_Gy_bin_width
	p_dose_bin_frequency__internal = p_dose_bin_frequency
	p_ion_response_bin_frequency__internal = p_ion_response_bin_frequency
	p_gamma_model__internal = p_gamma_model
	p_gamma_parameter__internal = p_gamma_parameter
	p_lethal_events_mode__internal = p_lethal_events_mode
	ret = _libAT.lib.AT_get_ion_efficiency_from_response_distribution(p_number_of_bins__internal.encode() if type(p_number_of_bins__internal) is str else p_number_of_bins__internal
			,p_dose_Gy_bin_position__internal.encode() if type(p_dose_Gy_bin_position__internal) is str else p_dose_Gy_bin_position__internal
			,p_dose_Gy_bin_width__internal.encode() if type(p_dose_Gy_bin_width__internal) is str else p_dose_Gy_bin_width__internal
			,p_dose_bin_frequency__internal.encode() if type(p_dose_bin_frequency__internal) is str else p_dose_bin_frequency__internal
			,p_ion_response_bin_frequency__internal.encode() if type(p_ion_response_bin_frequency__internal) is str else p_ion_response_bin_frequency__internal
			,p_gamma_model__internal.encode() if type(p_gamma_model__internal) is str else p_gamma_model__internal
			,p_gamma_parameter__internal.encode() if type(p_gamma_parameter__internal) is str else p_gamma_parameter__internal
			,p_lethal_events_mode__internal.encode() if type(p_lethal_events_mode__internal) is str else p_lethal_events_mode__internal
			)
	return ret
	

def AT_get_gamma_response(p_d_Gy, p_dd_Gy, p_f, p_f0, p_gamma_model, p_gamma_parameter, p_lethal_events_mode, p_S, p_S_HCP, p_S_gamma, p_efficiency):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns the detector / cell gamma response for a local dose distribution
	according to the chosen gamma response model, used by response model
	routines in AmTrack.c
	@param[in]  number_of_bins      number of bins in given local dose distribution
	@param[in]  d_Gy                local dose bin position in Gy (array of size number_of_bins)
	@param[in]  dd_Gy               local dose bin width in Gy (array of size number_of_bins)
	@param[in]  f                   local dose frequency (array of size number_of_bins)
	@param[in]  f0                  frequency of zero local dose
	@param[in]  gamma_model         gamma response model index
	@param[in]  gamma_parameter     vector holding necessary parameters for the chose gamma response model (array of size 9)
	@param[in]  lethal_events_mode  if true, allows to do calculations for cell survival
	@see  AmTrack.c/AT_IGK
	@param[out] S                   gamma responses for given bins (array of size number_of_bins)
	@param[out] S_HCP               HCP response for given local dose distribution (expectation value of S distribution)
	@param[out] S_gamma             gamma response for given local dose distribution (gamma response of expectation value of d distribution)
	@param[out] efficiency          RE = S_HCP/S_gamma for given local dose distribution
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_d_Gy,p_dd_Gy,p_f,p_gamma_parameter]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_bins
	declared_in_arr_param_size__number_of_bins = len(p_d_Gy)
	for in_array_argument in [p_d_Gy,p_dd_Gy,p_f]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_bins:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_S is passed correctly:
	if len(p_S) != len(p_f):
		out_array_auto_init = "\nWarning: OUT array parameter p_S was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_S.clear()
		p_S += [0]*len(p_f)
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_S_HCP)
	for in_array_argument in [p_S_HCP,p_S_gamma,p_efficiency]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_S_HCP, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_S_gamma, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_efficiency, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_S_HCP) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_S_HCP.clear()
		p_S_HCP += [0]
	
	if len(p_S_gamma) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_S_gamma.clear()
		p_S_gamma += [0]
	
	if len(p_efficiency) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_efficiency.clear()
		p_efficiency += [0]
	
	# Array sizes variables initialization:
	p_number_of_bins = len(p_d_Gy)
	p_number_of_bins__internal = p_number_of_bins
	p_d_Gy__internal = p_d_Gy
	p_dd_Gy__internal = p_dd_Gy
	p_f__internal = p_f
	p_f0__internal = p_f0
	p_gamma_model__internal = p_gamma_model
	p_gamma_parameter__internal = p_gamma_parameter
	p_lethal_events_mode__internal = p_lethal_events_mode
	p_S__internal = ffi.new("double[]", p_number_of_bins)
	for i,v in enumerate(p_S):
		p_S__internal[i] = v
	
	p_S_HCP__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_S_HCP):
		p_S_HCP__internal[i] = v
	
	p_S_gamma__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_S_gamma):
		p_S_gamma__internal[i] = v
	
	p_efficiency__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_efficiency):
		p_efficiency__internal[i] = v
	
	_libAT.lib.AT_get_gamma_response(p_number_of_bins__internal.encode() if type(p_number_of_bins__internal) is str else p_number_of_bins__internal
			,p_d_Gy__internal.encode() if type(p_d_Gy__internal) is str else p_d_Gy__internal
			,p_dd_Gy__internal.encode() if type(p_dd_Gy__internal) is str else p_dd_Gy__internal
			,p_f__internal.encode() if type(p_f__internal) is str else p_f__internal
			,p_f0__internal.encode() if type(p_f0__internal) is str else p_f0__internal
			,p_gamma_model__internal.encode() if type(p_gamma_model__internal) is str else p_gamma_model__internal
			,p_gamma_parameter__internal.encode() if type(p_gamma_parameter__internal) is str else p_gamma_parameter__internal
			,p_lethal_events_mode__internal.encode() if type(p_lethal_events_mode__internal) is str else p_lethal_events_mode__internal
			,p_S__internal.encode() if type(p_S__internal) is str else p_S__internal
			,p_S_HCP__internal.encode() if type(p_S_HCP__internal) is str else p_S_HCP__internal
			,p_S_gamma__internal.encode() if type(p_S_gamma__internal) is str else p_S_gamma__internal
			,p_efficiency__internal.encode() if type(p_efficiency__internal) is str else p_efficiency__internal
			)
	for i,v in enumerate(p_S__internal):
		p_S[i] = v
	
	for i,v in enumerate(p_S_HCP__internal):
		p_S_HCP[i] = v
	
	for i,v in enumerate(p_S_gamma__internal):
		p_S_gamma[i] = v
	
	for i,v in enumerate(p_efficiency__internal):
		p_efficiency[i] = v
	
	

def AT_run_CPPSC_method(p_E_MeV_u, p_particle_no, p_fluence_cm2_or_dose_Gy, p_material_no, p_stopping_power_source_no, p_rdd_model, p_rdd_parameters, p_er_model, p_gamma_model, p_gamma_parameters, p_N2, p_fluence_factor, p_write_output, p_shrink_tails, p_shrink_tails_under, p_adjust_N2, p_lethal_events_mode, p_relative_efficiency, p_d_check, p_S_HCP, p_S_gamma, p_mean_number_of_tracks_contrib, p_start_number_of_tracks_contrib, p_n_convolutions, p_lower_Jensen_bound, p_upper_Jensen_bound):
	"""
	Wrapping function generated for C language function documented as follows:
	@brief Algorithms for ATMs based on Compound Poisson Processes (CPP)
	Computes HCP response and relative efficiency/RBE using compound Poison processes and
	successive convolutions (CPP_SC, the 'SPIFF' algorithm)
	@param[in]      number_of_field_components     number of components in the mixed particle field
	@param[in]      E_MeV_u                        particle energy for each component in the mixed particle field [MeV/u] (array of size number_of_field_components)
	@param[in]      particle_no                    particle type for each component in the mixed particle field (array of size number_of_field_components)
	@see AT_DataParticle.h for definition
	@param[in]      fluence_cm2_or_dose_Gy         if positive, particle fluence for each component in the mixed particle field [1/cm2]; if negative, particle dose for each component in the mixed particle field [Gy] (array of size number_of_field_components)
	@param[in]      material_no                    index number for detector material
	@see AT_DataMaterial.h for definition
	@param[in]      stopping_power_source_no       TODO
	@param[in]      rdd_model                      index number for chosen radial dose distribution
	@param[in]      rdd_parameters                 parameters for chosen radial dose distribution (array of size 4)
	@see AT_RDD.h for definition
	@param[in]      er_model                       index number for chosen electron-range model
	@see AT_ElectronRange.h for definition
	@param[in]      gamma_model                    index number for chosen gamma response
	@param[in]      gamma_parameters               parameters for chosen gamma response (array of size 9)
	@see AT_GammaResponse.h for definition
	@param[in,out]  N2                             number of bins per factor of two for the dose scale of local dose histogram
	@param[in]      fluence_factor                 factor to scale the fluences / doses given in "fluence_cm2_or_dose_Gy" with
	@param[in]      write_output                   if true, a log-file is written to "SuccessiveConvolutions.txt" in the working directory
	@param[in]      shrink_tails                   if true, tails of the local dose distribution, contributing less than "shrink_tails_under" are cut
	@param[in]      shrink_tails_under             limit for tail cutting in local dose distribution
	@param[in]      adjust_N2                      if true, "N2" will be increase if necessary at high fluence to ensure sufficient local dose histogram resolution
	@param[in]      lethal_events_mode             if true, computations are done for dependent subtargets
	@param[out]     relative_efficiency            particle response at dose D / gamma response at dose D
	@param[out]     d_check                        sanity check:  total dose (in Gy) as returned by the algorithm
	@param[out]     S_HCP                          absolute particle response
	@param[out]     S_gamma                        absolute gamma response
	@param[out]     mean_number_of_tracks_contrib  mean number of tracks contributing to representative point
	@param[out]     start_number_of_tracks_contrib low fluence approximation for mean number of tracks contributing to representative point (start value for successive convolutions)
	@param[out]     n_convolutions                 number of convolutions performed to reach requested dose/fluence
	@param[out]     lower_Jensen_bound             lower bound for Jensen's inequity
	@param[out]     upper_Jensen_bound             upper bound for Jensen's inequity
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2_or_dose_Gy,p_rdd_parameters,p_gamma_parameters]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2_or_dose_Gy]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_relative_efficiency)
	for in_array_argument in [p_relative_efficiency,p_d_check,p_S_HCP,p_S_gamma,p_mean_number_of_tracks_contrib,p_start_number_of_tracks_contrib,p_n_convolutions,p_lower_Jensen_bound,p_upper_Jensen_bound]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_relative_efficiency, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_d_check, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_S_HCP, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_S_gamma, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_mean_number_of_tracks_contrib, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_start_number_of_tracks_contrib, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_n_convolutions, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_lower_Jensen_bound, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_upper_Jensen_bound, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_relative_efficiency) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_relative_efficiency.clear()
		p_relative_efficiency += [0]
	
	if len(p_d_check) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_d_check.clear()
		p_d_check += [0]
	
	if len(p_S_HCP) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_S_HCP.clear()
		p_S_HCP += [0]
	
	if len(p_S_gamma) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_S_gamma.clear()
		p_S_gamma += [0]
	
	if len(p_mean_number_of_tracks_contrib) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_mean_number_of_tracks_contrib.clear()
		p_mean_number_of_tracks_contrib += [0]
	
	if len(p_start_number_of_tracks_contrib) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_start_number_of_tracks_contrib.clear()
		p_start_number_of_tracks_contrib += [0]
	
	if len(p_n_convolutions) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_n_convolutions.clear()
		p_n_convolutions += [0]
	
	if len(p_lower_Jensen_bound) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_lower_Jensen_bound.clear()
		p_lower_Jensen_bound += [0]
	
	if len(p_upper_Jensen_bound) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_upper_Jensen_bound.clear()
		p_upper_Jensen_bound += [0]
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2_or_dose_Gy__internal = p_fluence_cm2_or_dose_Gy
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_rdd_model__internal = p_rdd_model
	p_rdd_parameters__internal = p_rdd_parameters
	p_er_model__internal = p_er_model
	p_gamma_model__internal = p_gamma_model
	p_gamma_parameters__internal = p_gamma_parameters
	p_N2__internal = p_N2
	p_fluence_factor__internal = p_fluence_factor
	p_write_output__internal = p_write_output
	p_shrink_tails__internal = p_shrink_tails
	p_shrink_tails_under__internal = p_shrink_tails_under
	p_adjust_N2__internal = p_adjust_N2
	p_lethal_events_mode__internal = p_lethal_events_mode
	p_relative_efficiency__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_relative_efficiency):
		p_relative_efficiency__internal[i] = v
	
	p_d_check__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_d_check):
		p_d_check__internal[i] = v
	
	p_S_HCP__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_S_HCP):
		p_S_HCP__internal[i] = v
	
	p_S_gamma__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_S_gamma):
		p_S_gamma__internal[i] = v
	
	p_mean_number_of_tracks_contrib__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_mean_number_of_tracks_contrib):
		p_mean_number_of_tracks_contrib__internal[i] = v
	
	p_start_number_of_tracks_contrib__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_start_number_of_tracks_contrib):
		p_start_number_of_tracks_contrib__internal[i] = v
	
	p_n_convolutions__internal = ffi.new("long[]", 1)
	for i,v in enumerate(p_n_convolutions):
		p_n_convolutions__internal[i] = v
	
	p_lower_Jensen_bound__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_lower_Jensen_bound):
		p_lower_Jensen_bound__internal[i] = v
	
	p_upper_Jensen_bound__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_upper_Jensen_bound):
		p_upper_Jensen_bound__internal[i] = v
	
	_libAT.lib.AT_run_CPPSC_method(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2_or_dose_Gy__internal.encode() if type(p_fluence_cm2_or_dose_Gy__internal) is str else p_fluence_cm2_or_dose_Gy__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_rdd_model__internal.encode() if type(p_rdd_model__internal) is str else p_rdd_model__internal
			,p_rdd_parameters__internal.encode() if type(p_rdd_parameters__internal) is str else p_rdd_parameters__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_gamma_model__internal.encode() if type(p_gamma_model__internal) is str else p_gamma_model__internal
			,p_gamma_parameters__internal.encode() if type(p_gamma_parameters__internal) is str else p_gamma_parameters__internal
			,p_N2__internal.encode() if type(p_N2__internal) is str else p_N2__internal
			,p_fluence_factor__internal.encode() if type(p_fluence_factor__internal) is str else p_fluence_factor__internal
			,p_write_output__internal.encode() if type(p_write_output__internal) is str else p_write_output__internal
			,p_shrink_tails__internal.encode() if type(p_shrink_tails__internal) is str else p_shrink_tails__internal
			,p_shrink_tails_under__internal.encode() if type(p_shrink_tails_under__internal) is str else p_shrink_tails_under__internal
			,p_adjust_N2__internal.encode() if type(p_adjust_N2__internal) is str else p_adjust_N2__internal
			,p_lethal_events_mode__internal.encode() if type(p_lethal_events_mode__internal) is str else p_lethal_events_mode__internal
			,p_relative_efficiency__internal.encode() if type(p_relative_efficiency__internal) is str else p_relative_efficiency__internal
			,p_d_check__internal.encode() if type(p_d_check__internal) is str else p_d_check__internal
			,p_S_HCP__internal.encode() if type(p_S_HCP__internal) is str else p_S_HCP__internal
			,p_S_gamma__internal.encode() if type(p_S_gamma__internal) is str else p_S_gamma__internal
			,p_mean_number_of_tracks_contrib__internal.encode() if type(p_mean_number_of_tracks_contrib__internal) is str else p_mean_number_of_tracks_contrib__internal
			,p_start_number_of_tracks_contrib__internal.encode() if type(p_start_number_of_tracks_contrib__internal) is str else p_start_number_of_tracks_contrib__internal
			,p_n_convolutions__internal.encode() if type(p_n_convolutions__internal) is str else p_n_convolutions__internal
			,p_lower_Jensen_bound__internal.encode() if type(p_lower_Jensen_bound__internal) is str else p_lower_Jensen_bound__internal
			,p_upper_Jensen_bound__internal.encode() if type(p_upper_Jensen_bound__internal) is str else p_upper_Jensen_bound__internal
			)
	p_N2 = p_N2__internal
	for i,v in enumerate(p_relative_efficiency__internal):
		p_relative_efficiency[i] = v
	
	for i,v in enumerate(p_d_check__internal):
		p_d_check[i] = v
	
	for i,v in enumerate(p_S_HCP__internal):
		p_S_HCP[i] = v
	
	for i,v in enumerate(p_S_gamma__internal):
		p_S_gamma[i] = v
	
	for i,v in enumerate(p_mean_number_of_tracks_contrib__internal):
		p_mean_number_of_tracks_contrib[i] = v
	
	for i,v in enumerate(p_start_number_of_tracks_contrib__internal):
		p_start_number_of_tracks_contrib[i] = v
	
	for i,v in enumerate(p_n_convolutions__internal):
		p_n_convolutions[i] = v
	
	for i,v in enumerate(p_lower_Jensen_bound__internal):
		p_lower_Jensen_bound[i] = v
	
	for i,v in enumerate(p_upper_Jensen_bound__internal):
		p_upper_Jensen_bound[i] = v
	
	

def AT_run_CPPSS_method(p_E_MeV_u, p_particle_no, p_fluence_cm2_or_dose_Gy, p_material_no, p_stopping_power_source_no, p_RDD_model, p_RDD_parameters, p_ER_model, p_gamma_model, p_gamma_parameters, p_n_runs, p_N2, p_fluence_factor, p_write_output, p_importance_sampling, p_results):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes HCP response and RE/RBE using compound Poison process and
	statistical sampling (CPP_SS, the 'SPISS' algorithm)
	@param[in]  number_of_field_components  number of particle types in the mixed particle field
	@param[in]  E_MeV_u             energy of particles in the mixed particle field (array of size number_of_field_components)
	@param[in]  particle_no         type of the particles in the mixed particle field (array of size number_of_field_components)
	@see          AT_DataParticle.h for definition
	@param[in]  fluence_cm2_or_dose_Gy         fluences for the given particles, doses in Gy if negative (array of size number_of_field_components)
	@param[in]  material_no         index number for detector material
	@see          AT_DataMaterial.h for definition
	@param[in]  stopping_power_source_no         TODO
	@param[in]  RDD_model           index number for chosen radial dose distribution
	@param[in]  RDD_parameters      parameters for chosen radial dose distribution (array of size 4)
	@see          AT_RDD.h for definition
	@param[in]  ER_model            index number for chosen electron-range model
	@see          AT_ElectronRange.h for definition
	@param[in]  gamma_model         index number for chosen gamma response
	@param[in]  gamma_parameters    parameters for chosen gamma response (array of size 9)
	@see          AT_GammaResponse.h for definition
	@param[in]  n_runs              (algorithm specific) number of points sampled for local dose distribution
	@param[in]  N2                  (algorithm specific) number of bins per factor of two in local dose array
	@param[in]  fluence_factor      factor to scale the fluences given as "fluence_cm2" with
	@param[in]  write_output        if true, a protocol is written to "SuccessiveConvolutions.txt" in the working directory
	@param[in]  importance_sampling if unequal zero importance sampling will be applied to the single impact local dose distribution
	@param[out]  results            array of size 10 to be allocated by the user which will be used to return the results\n
	results[0]    efficiency      (algorithm independent)  main result:   particle response at dose D / gamma response at dose D\n
	results[1]    d_check         (algorithm independent)  sanity check:  total dose (in Gy) as returned by the algorithm\n
	results[2]    S_HCP           (algorithm independent)  absolute particle response\n
	results[3]    S_gamma         (algorithm independent)  absolute gamma response\n
	results[4]    not used        (algorithm independent)\n
	results[5]    not_used        (algorithm specific)\n
	results[6]    not used        (algorithm specific)\n
	results[7]    not_used        (algorithm specific)\n
	results[8]    not used        (algorithm specific)\n
	results[9]    not used        (algorithm specific)\n
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2_or_dose_Gy,p_RDD_parameters,p_gamma_parameters]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2_or_dose_Gy]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_results, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_results) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_results.clear()
		p_results += [0]
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2_or_dose_Gy__internal = p_fluence_cm2_or_dose_Gy
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_RDD_model__internal = p_RDD_model
	p_RDD_parameters__internal = p_RDD_parameters
	p_ER_model__internal = p_ER_model
	p_gamma_model__internal = p_gamma_model
	p_gamma_parameters__internal = p_gamma_parameters
	p_n_runs__internal = p_n_runs
	p_N2__internal = p_N2
	p_fluence_factor__internal = p_fluence_factor
	p_write_output__internal = p_write_output
	p_importance_sampling__internal = p_importance_sampling
	p_results__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_results):
		p_results__internal[i] = v
	
	_libAT.lib.AT_run_CPPSS_method(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2_or_dose_Gy__internal.encode() if type(p_fluence_cm2_or_dose_Gy__internal) is str else p_fluence_cm2_or_dose_Gy__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_RDD_model__internal.encode() if type(p_RDD_model__internal) is str else p_RDD_model__internal
			,p_RDD_parameters__internal.encode() if type(p_RDD_parameters__internal) is str else p_RDD_parameters__internal
			,p_ER_model__internal.encode() if type(p_ER_model__internal) is str else p_ER_model__internal
			,p_gamma_model__internal.encode() if type(p_gamma_model__internal) is str else p_gamma_model__internal
			,p_gamma_parameters__internal.encode() if type(p_gamma_parameters__internal) is str else p_gamma_parameters__internal
			,p_n_runs__internal.encode() if type(p_n_runs__internal) is str else p_n_runs__internal
			,p_N2__internal.encode() if type(p_N2__internal) is str else p_N2__internal
			,p_fluence_factor__internal.encode() if type(p_fluence_factor__internal) is str else p_fluence_factor__internal
			,p_write_output__internal.encode() if type(p_write_output__internal) is str else p_write_output__internal
			,p_importance_sampling__internal.encode() if type(p_importance_sampling__internal) is str else p_importance_sampling__internal
			,p_results__internal.encode() if type(p_results__internal) is str else p_results__internal
			)
	for i,v in enumerate(p_results__internal):
		p_results[i] = v
	
	

def AT_KatzModel_sigma_um2_single(p_E_MeV_u, p_particle_no, p_m, p_D0_Gy, p_a0_um, p_katz_model_flavour, p_stop_power_source):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates inactivation cross-section (sigma) for given energy.
	Sigma is evaluated by double integration:
	- first of radial dose distribution (over site with radius a0)
	- second of inactivation probability (over all radii)
	Sigma can be calculated using 3 possible combination of radial dose and electron range models
	@param[in] E_MeV_u
	@param[in] particle_no
	@param[in] m
	@param[in] D0_Gy
	@param[in] a0_um
	@param[in] katz_model_flavour
	@param[in] stop_power_source
	@return inactivation cross-section (sigma) [um2]
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_m__internal = p_m
	p_D0_Gy__internal = p_D0_Gy
	p_a0_um__internal = p_a0_um
	p_katz_model_flavour__internal = p_katz_model_flavour
	p_stop_power_source__internal = p_stop_power_source
	ret = _libAT.lib.AT_KatzModel_sigma_um2_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_m__internal.encode() if type(p_m__internal) is str else p_m__internal
			,p_D0_Gy__internal.encode() if type(p_D0_Gy__internal) is str else p_D0_Gy__internal
			,p_a0_um__internal.encode() if type(p_a0_um__internal) is str else p_a0_um__internal
			,p_katz_model_flavour__internal.encode() if type(p_katz_model_flavour__internal) is str else p_katz_model_flavour__internal
			,p_stop_power_source__internal.encode() if type(p_stop_power_source__internal) is str else p_stop_power_source__internal
			)
	return ret
	

def AT_KatzModel_sigma_um2(p_E_MeV_u, p_particle_no, p_m, p_D0_Gy, p_a0_um, p_katz_model_flavour, p_stop_power_source, p_sigma_um2):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates inactivation cross-section (sigma) for given energy.
	Vectorised version of AT_KatzModel_sigma_um2_single
	@param[in] n
	@param[in] E_MeV_u  (array of size n)
	@param[in] particle_no
	@param[in] m
	@param[in] D0_Gy
	@param[in] a0_um
	@param[in] katz_model_flavour
	@param[in] stop_power_source
	@param[out] sigma_um2 (array of size n)
	@return status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_sigma_um2 is passed correctly:
	if len(p_sigma_um2) != len(p_E_MeV_u):
		out_array_auto_init = "\nWarning: OUT array parameter p_sigma_um2 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_sigma_um2.clear()
		p_sigma_um2 += [0]*len(p_E_MeV_u)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_m__internal = p_m
	p_D0_Gy__internal = p_D0_Gy
	p_a0_um__internal = p_a0_um
	p_katz_model_flavour__internal = p_katz_model_flavour
	p_stop_power_source__internal = p_stop_power_source
	p_sigma_um2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_sigma_um2):
		p_sigma_um2__internal[i] = v
	
	ret = _libAT.lib.AT_KatzModel_sigma_um2(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_m__internal.encode() if type(p_m__internal) is str else p_m__internal
			,p_D0_Gy__internal.encode() if type(p_D0_Gy__internal) is str else p_D0_Gy__internal
			,p_a0_um__internal.encode() if type(p_a0_um__internal) is str else p_a0_um__internal
			,p_katz_model_flavour__internal.encode() if type(p_katz_model_flavour__internal) is str else p_katz_model_flavour__internal
			,p_stop_power_source__internal.encode() if type(p_stop_power_source__internal) is str else p_stop_power_source__internal
			,p_sigma_um2__internal.encode() if type(p_sigma_um2__internal) is str else p_sigma_um2__internal
			)
	for i,v in enumerate(p_sigma_um2__internal):
		p_sigma_um2[i] = v
	
	return ret
	

def AT_KatzModel_sigma_approx_um2_single(p_E_MeV_u, p_particle_no, p_m, p_sigma0_um2, p_kappa, p_katz_model_flavour):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates approximated inactivation cross-section (sigma) for given energy.
	approximation via "trkwid" function
	Sigma can be calculated using 2 possible combination of radial dose and electron range models
	@param[in] E_MeV_u
	@param[in] particle_no
	@param[in] m
	@param[in] sigma0_um2
	@param[in] kappa
	@param[in] katz_model_flavour
	@return inactivation cross-section (sigma) [um2]
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_m__internal = p_m
	p_sigma0_um2__internal = p_sigma0_um2
	p_kappa__internal = p_kappa
	p_katz_model_flavour__internal = p_katz_model_flavour
	ret = _libAT.lib.AT_KatzModel_sigma_approx_um2_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_m__internal.encode() if type(p_m__internal) is str else p_m__internal
			,p_sigma0_um2__internal.encode() if type(p_sigma0_um2__internal) is str else p_sigma0_um2__internal
			,p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_katz_model_flavour__internal.encode() if type(p_katz_model_flavour__internal) is str else p_katz_model_flavour__internal
			)
	return ret
	

def AT_KatzModel_sigma_approx_um2(p_E_MeV_u, p_particle_no, p_m, p_sigma0_um2, p_kappa, p_katz_model_flavour, p_sigma_um2):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates approximated inactivation cross-section (sigma) for given energy.
	Vectorised version of AT_KatzModel_sigma_approx_um2_single
	@param[in] n
	@param[in] E_MeV_u (array of size n)
	@param[in] particle_no
	@param[in] m
	@param[in] sigma0_um2
	@param[in] kappa
	@param[in] katz_model_flavour
	@param[out] sigma_um2 (array of size n)
	@return status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_sigma_um2 is passed correctly:
	if len(p_sigma_um2) != len(p_E_MeV_u):
		out_array_auto_init = "\nWarning: OUT array parameter p_sigma_um2 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_sigma_um2.clear()
		p_sigma_um2 += [0]*len(p_E_MeV_u)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_m__internal = p_m
	p_sigma0_um2__internal = p_sigma0_um2
	p_kappa__internal = p_kappa
	p_katz_model_flavour__internal = p_katz_model_flavour
	p_sigma_um2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_sigma_um2):
		p_sigma_um2__internal[i] = v
	
	ret = _libAT.lib.AT_KatzModel_sigma_approx_um2(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_m__internal.encode() if type(p_m__internal) is str else p_m__internal
			,p_sigma0_um2__internal.encode() if type(p_sigma0_um2__internal) is str else p_sigma0_um2__internal
			,p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_katz_model_flavour__internal.encode() if type(p_katz_model_flavour__internal) is str else p_katz_model_flavour__internal
			,p_sigma_um2__internal.encode() if type(p_sigma_um2__internal) is str else p_sigma_um2__internal
			)
	for i,v in enumerate(p_sigma_um2__internal):
		p_sigma_um2[i] = v
	
	return ret
	

def AT_KatzModel_survival_single(p_dose_Gy, p_E_MeV_u, p_particle_no, p_m, p_D0_Gy, p_sigma0_um2, p_kappa, p_a0_um, p_katz_model_flavour, p_approximate, p_stopping_power_source_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates cell survival for given dose, energy and particle type.
	@param[in] dose_Gy
	@param[in] E_MeV_u
	@param[in] particle_no
	@param[in] m
	@param[in] D0_Gy
	@param[in] sigma0_um2
	@param[in] kappa
	@param[in] a0_um
	@param[in] katz_model_flavour
	@param[in] approximate
	@param[in] stopping_power_source_no
	@return cell survival
	"""
	p_dose_Gy__internal = p_dose_Gy
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_m__internal = p_m
	p_D0_Gy__internal = p_D0_Gy
	p_sigma0_um2__internal = p_sigma0_um2
	p_kappa__internal = p_kappa
	p_a0_um__internal = p_a0_um
	p_katz_model_flavour__internal = p_katz_model_flavour
	p_approximate__internal = p_approximate
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	ret = _libAT.lib.AT_KatzModel_survival_single(p_dose_Gy__internal.encode() if type(p_dose_Gy__internal) is str else p_dose_Gy__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_m__internal.encode() if type(p_m__internal) is str else p_m__internal
			,p_D0_Gy__internal.encode() if type(p_D0_Gy__internal) is str else p_D0_Gy__internal
			,p_sigma0_um2__internal.encode() if type(p_sigma0_um2__internal) is str else p_sigma0_um2__internal
			,p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_a0_um__internal.encode() if type(p_a0_um__internal) is str else p_a0_um__internal
			,p_katz_model_flavour__internal.encode() if type(p_katz_model_flavour__internal) is str else p_katz_model_flavour__internal
			,p_approximate__internal.encode() if type(p_approximate__internal) is str else p_approximate__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			)
	return ret
	

def AT_KatzModel_survival(p_dose_Gy, p_E_MeV_u, p_particle_no, p_m, p_D0_Gy, p_sigma0_um2, p_kappa, p_a0_um, p_katz_model_flavour, p_approximate, p_stopping_power_source_no, p_survival):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates cell survival for given dose, energy and particle type.
	Vectorised version of AT_KatzModel_survival_single
	@param[in] n
	@param[in] dose_Gy (array of size n)
	@param[in] E_MeV_u
	@param[in] particle_no
	@param[in] m
	@param[in] D0_Gy
	@param[in] sigma0_um2
	@param[in] kappa
	@param[in] a0_um
	@param[in] katz_model_flavour
	@param[in] approximate
	@param[in] stopping_power_source_no
	@param[out] survival (array of size n)
	@return status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_dose_Gy]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_survival is passed correctly:
	if len(p_survival) != len(p_dose_Gy):
		out_array_auto_init = "\nWarning: OUT array parameter p_survival was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_survival.clear()
		p_survival += [0]*len(p_dose_Gy)
	
	# Array sizes variables initialization:
	p_n = len(p_dose_Gy)
	p_n__internal = p_n
	p_dose_Gy__internal = p_dose_Gy
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_m__internal = p_m
	p_D0_Gy__internal = p_D0_Gy
	p_sigma0_um2__internal = p_sigma0_um2
	p_kappa__internal = p_kappa
	p_a0_um__internal = p_a0_um
	p_katz_model_flavour__internal = p_katz_model_flavour
	p_approximate__internal = p_approximate
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_survival__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_survival):
		p_survival__internal[i] = v
	
	ret = _libAT.lib.AT_KatzModel_survival(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_dose_Gy__internal.encode() if type(p_dose_Gy__internal) is str else p_dose_Gy__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_m__internal.encode() if type(p_m__internal) is str else p_m__internal
			,p_D0_Gy__internal.encode() if type(p_D0_Gy__internal) is str else p_D0_Gy__internal
			,p_sigma0_um2__internal.encode() if type(p_sigma0_um2__internal) is str else p_sigma0_um2__internal
			,p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_a0_um__internal.encode() if type(p_a0_um__internal) is str else p_a0_um__internal
			,p_katz_model_flavour__internal.encode() if type(p_katz_model_flavour__internal) is str else p_katz_model_flavour__internal
			,p_approximate__internal.encode() if type(p_approximate__internal) is str else p_approximate__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_survival__internal.encode() if type(p_survival__internal) is str else p_survival__internal
			)
	for i,v in enumerate(p_survival__internal):
		p_survival[i] = v
	
	return ret
	

def AT_KatzModel_RBE_single(p_E_MeV_u, p_particle_no, p_m, p_D0_Gy, p_sigma0_um2, p_kappa, p_a0_um, p_katz_model_flavour, p_approximate, p_stopping_power_source_no, p_level):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates RBE for given energy and particle type.
	@param[in] E_MeV_u
	@param[in] particle_no
	@param[in] m
	@param[in] D0_Gy
	@param[in] sigma0_um2
	@param[in] kappa
	@param[in] a0_um
	@param[in] katz_model_flavour
	@param[in] approximate
	@param[in] stopping_power_source_no
	@param[in] level
	@return rbe
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_m__internal = p_m
	p_D0_Gy__internal = p_D0_Gy
	p_sigma0_um2__internal = p_sigma0_um2
	p_kappa__internal = p_kappa
	p_a0_um__internal = p_a0_um
	p_katz_model_flavour__internal = p_katz_model_flavour
	p_approximate__internal = p_approximate
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_level__internal = p_level
	ret = _libAT.lib.AT_KatzModel_RBE_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_m__internal.encode() if type(p_m__internal) is str else p_m__internal
			,p_D0_Gy__internal.encode() if type(p_D0_Gy__internal) is str else p_D0_Gy__internal
			,p_sigma0_um2__internal.encode() if type(p_sigma0_um2__internal) is str else p_sigma0_um2__internal
			,p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_a0_um__internal.encode() if type(p_a0_um__internal) is str else p_a0_um__internal
			,p_katz_model_flavour__internal.encode() if type(p_katz_model_flavour__internal) is str else p_katz_model_flavour__internal
			,p_approximate__internal.encode() if type(p_approximate__internal) is str else p_approximate__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_level__internal.encode() if type(p_level__internal) is str else p_level__internal
			)
	return ret
	

def AT_KatzModel_RBE(p_E_MeV_u, p_particle_no, p_m, p_D0_Gy, p_sigma0_um2, p_kappa, p_a0_um, p_katz_model_flavour, p_approximate, p_stopping_power_source_no, p_level, p_rbe):
	"""
	Wrapping function generated for C language function documented as follows:
	Calculates RBE for given energy and particle type.
	Vectorised version of AT_KatzModel_RBE_single
	@param[in] n
	@param[in] E_MeV_u (array of size n)
	@param[in] particle_no
	@param[in] m
	@param[in] D0_Gy
	@param[in] sigma0_um2
	@param[in] kappa
	@param[in] a0_um
	@param[in] katz_model_flavour
	@param[in] approximate
	@param[in] stopping_power_source_no
	@param[in] level
	@param[out] rbe (array of size n)
	@return status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_rbe is passed correctly:
	if len(p_rbe) != len(p_E_MeV_u):
		out_array_auto_init = "\nWarning: OUT array parameter p_rbe was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_rbe.clear()
		p_rbe += [0]*len(p_E_MeV_u)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_m__internal = p_m
	p_D0_Gy__internal = p_D0_Gy
	p_sigma0_um2__internal = p_sigma0_um2
	p_kappa__internal = p_kappa
	p_a0_um__internal = p_a0_um
	p_katz_model_flavour__internal = p_katz_model_flavour
	p_approximate__internal = p_approximate
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_level__internal = p_level
	p_rbe__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_rbe):
		p_rbe__internal[i] = v
	
	ret = _libAT.lib.AT_KatzModel_RBE(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_m__internal.encode() if type(p_m__internal) is str else p_m__internal
			,p_D0_Gy__internal.encode() if type(p_D0_Gy__internal) is str else p_D0_Gy__internal
			,p_sigma0_um2__internal.encode() if type(p_sigma0_um2__internal) is str else p_sigma0_um2__internal
			,p_kappa__internal.encode() if type(p_kappa__internal) is str else p_kappa__internal
			,p_a0_um__internal.encode() if type(p_a0_um__internal) is str else p_a0_um__internal
			,p_katz_model_flavour__internal.encode() if type(p_katz_model_flavour__internal) is str else p_katz_model_flavour__internal
			,p_approximate__internal.encode() if type(p_approximate__internal) is str else p_approximate__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_level__internal.encode() if type(p_level__internal) is str else p_level__internal
			,p_rbe__internal.encode() if type(p_rbe__internal) is str else p_rbe__internal
			)
	for i,v in enumerate(p_rbe__internal):
		p_rbe[i] = v
	
	return ret
	

def AT_E_MeV_u_from_E_MeV(p_E_MeV, p_particle_no):
	"""
	Wrapping function generated for C language function documented as follows:
	@brief Physics related routines
	Returns energy per nucleon from kinetic energy of particle
	@param[in]  E_MeV                    kinetic energy of particle [MeV]
	@param[in]  particle_no              type of the particle
	@return     E_MeV_u                  energy of particle per nucleon [MeV/u]
	"""
	p_E_MeV__internal = p_E_MeV
	p_particle_no__internal = p_particle_no
	ret = _libAT.lib.AT_E_MeV_u_from_E_MeV(p_E_MeV__internal.encode() if type(p_E_MeV__internal) is str else p_E_MeV__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			)
	return ret
	

def AT_E_MeV_from_E_MeV_u(p_E_MeV_u, p_particle_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns energy per nucleon from kinetic energy of particle
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@param[in]  particle_no              type of the particle
	@return     E_MeV                    kinetic energy of particle [MeV]
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	ret = _libAT.lib.AT_E_MeV_from_E_MeV_u(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			)
	return ret
	

def AT_beta_from_E_single(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns relativistic speed for single value of energy
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@return     beta                     relative particle speed beta = v/c
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_beta_from_E_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_beta_from_E(p_E_MeV_u, p_beta):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns relativistic speed for many particles
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  vector of energies of particle per nucleon [MeV/u] (array of size n)
	@param[out] beta                     vector of relative particle speed beta = v/c (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_beta is passed correctly:
	if len(p_beta) != len(p_E_MeV_u):
		out_array_auto_init = "\nWarning: OUT array parameter p_beta was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_beta.clear()
		p_beta += [0]*len(p_E_MeV_u)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_beta__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_beta):
		p_beta__internal[i] = v
	
	ret = _libAT.lib.AT_beta_from_E(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			)
	for i,v in enumerate(p_beta__internal):
		p_beta[i] = v
	
	return ret
	

def AT_E_from_beta_single(p_beta):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns energy per nucleon of particle with relative speed beta
	@param[in]  beta                     relative particle speed beta = v/c
	@return                              energy of particle per nucleon [MeV/u]
	"""
	p_beta__internal = p_beta
	ret = _libAT.lib.AT_E_from_beta_single(p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			)
	return ret
	

def AT_E_from_beta(p_beta, p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns energy per nucleon of particle with relativistic speed beta
	@param[in]  n                        number of particles
	@param[in]  beta                     vector of relative particle speed beta = v/c (array of size n)
	@param[out] E_MeV_u                  vector of energies of particle per nucleon [MeV/u] (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_beta]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_E_MeV_u is passed correctly:
	if len(p_E_MeV_u) != len(p_beta):
		out_array_auto_init = "\nWarning: OUT array parameter p_E_MeV_u was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_E_MeV_u.clear()
		p_E_MeV_u += [0]*len(p_beta)
	
	# Array sizes variables initialization:
	p_n = len(p_beta)
	p_n__internal = p_n
	p_beta__internal = p_beta
	p_E_MeV_u__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_E_MeV_u):
		p_E_MeV_u__internal[i] = v
	
	ret = _libAT.lib.AT_E_from_beta(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	for i,v in enumerate(p_E_MeV_u__internal):
		p_E_MeV_u[i] = v
	
	return ret
	

def AT_E_from_gamma_single(p_gamma):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns energy for single value of relativistic gamma
	@param[in]  gamma
	@return     E_MeV_u                  energy of particle per nucleon [MeV/u]
	"""
	p_gamma__internal = p_gamma
	ret = _libAT.lib.AT_E_from_gamma_single(p_gamma__internal.encode() if type(p_gamma__internal) is str else p_gamma__internal
			)
	return ret
	

def AT_E_from_gamma(p_gamma, p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns energy from relativistic gamma
	@param[in]  n                        number of particles
	@param[in]  gamma                    vector of results (array of size n)
	@param[out] E_MeV_u                  vector of energies of particle per nucleon [MeV/u] (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_gamma]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_E_MeV_u is passed correctly:
	if len(p_E_MeV_u) != len(p_gamma):
		out_array_auto_init = "\nWarning: OUT array parameter p_E_MeV_u was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_E_MeV_u.clear()
		p_E_MeV_u += [0]*len(p_gamma)
	
	# Array sizes variables initialization:
	p_n = len(p_gamma)
	p_n__internal = p_n
	p_gamma__internal = p_gamma
	p_E_MeV_u__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_E_MeV_u):
		p_E_MeV_u__internal[i] = v
	
	ret = _libAT.lib.AT_E_from_gamma(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_gamma__internal.encode() if type(p_gamma__internal) is str else p_gamma__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	for i,v in enumerate(p_E_MeV_u__internal):
		p_E_MeV_u[i] = v
	
	return ret
	

def AT_E_MeV_u_from_momentum_single(p_momentum_MeV_c_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns energy per nucleon of particle with given momentum per nucleon
	@param[in]  momentum_MeV_c_u         momentum per particle [MeV/c]
	@return                              energy of particle per nucleon [MeV/u]
	"""
	p_momentum_MeV_c_u__internal = p_momentum_MeV_c_u
	ret = _libAT.lib.AT_E_MeV_u_from_momentum_single(p_momentum_MeV_c_u__internal.encode() if type(p_momentum_MeV_c_u__internal) is str else p_momentum_MeV_c_u__internal
			)
	return ret
	

def AT_E_MeV_u_from_momentum_MeV_c_u(p_momentum_MeV_c_u, p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns energy per nucleon for particles with given momentum per nucleon
	@param[in]  n                        number of particles
	@param[in]  momentum_MeV_c_u         vector of particle momenta per nucleon [MeV/c], (array of size n)
	@param[out] E_MeV_u                  vector of energies of particle per nucleon [MeV/u], (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_momentum_MeV_c_u]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_E_MeV_u is passed correctly:
	if len(p_E_MeV_u) != len(p_momentum_MeV_c_u):
		out_array_auto_init = "\nWarning: OUT array parameter p_E_MeV_u was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_E_MeV_u.clear()
		p_E_MeV_u += [0]*len(p_momentum_MeV_c_u)
	
	# Array sizes variables initialization:
	p_n = len(p_momentum_MeV_c_u)
	p_n__internal = p_n
	p_momentum_MeV_c_u__internal = p_momentum_MeV_c_u
	p_E_MeV_u__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_E_MeV_u):
		p_E_MeV_u__internal[i] = v
	
	ret = _libAT.lib.AT_E_MeV_u_from_momentum_MeV_c_u(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_momentum_MeV_c_u__internal.encode() if type(p_momentum_MeV_c_u__internal) is str else p_momentum_MeV_c_u__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	for i,v in enumerate(p_E_MeV_u__internal):
		p_E_MeV_u[i] = v
	
	return ret
	

def AT_gamma_from_E_single(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns relativistic gamma for single value of energy
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@return     gamma
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_gamma_from_E_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_gamma_from_E(p_E_MeV_u, p_gamma):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns relativistic gamma
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  vector of energies of particle per nucleon [MeV/u] (array of size n)
	@param[out] gamma                    vector of results (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_gamma is passed correctly:
	if len(p_gamma) != len(p_E_MeV_u):
		out_array_auto_init = "\nWarning: OUT array parameter p_gamma was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_gamma.clear()
		p_gamma += [0]*len(p_E_MeV_u)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_gamma__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_gamma):
		p_gamma__internal[i] = v
	
	ret = _libAT.lib.AT_gamma_from_E(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_gamma__internal.encode() if type(p_gamma__internal) is str else p_gamma__internal
			)
	for i,v in enumerate(p_gamma__internal):
		p_gamma[i] = v
	
	return ret
	

def AT_effective_charge_from_beta_single(p_beta, p_Z):
	"""
	Wrapping function generated for C language function documented as follows:
	Effective charge according to Barkas-Bethe-approximation:
	Zeff = Z *[1- exp( -125 * beta / Z^(2/3) )]
	calculated for particle with given relative speed beta
	@param[in]  beta                     relative particle speed beta = v/c
	@param[in]  Z                        atomic number Z of ion
	@return     effective_charge of ion
	"""
	p_beta__internal = p_beta
	p_Z__internal = p_Z
	ret = _libAT.lib.AT_effective_charge_from_beta_single(p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			)
	return ret
	

def AT_effective_charge_from_beta(p_beta, p_Z, p_effective_charge):
	"""
	Wrapping function generated for C language function documented as follows:
	Effective charge according to Barkas-Bethe approximation:
	Zeff = Z *[1-exp( -125 * beta / Z^(2/3) )]
	calculated for particle with given relative speed beta
	@param[in]  n                        number of particles
	@param[in]  beta                     vector of relative particle speed beta = v/c (array of size n)
	@param[in]  Z                        atomic number Z of ion (array of size n)
	@param[out] effective_charge of ion (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_beta,p_Z]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_beta)
	for in_array_argument in [p_beta,p_Z]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_effective_charge is passed correctly:
	if len(p_effective_charge) != len(p_Z):
		out_array_auto_init = "\nWarning: OUT array parameter p_effective_charge was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_effective_charge.clear()
		p_effective_charge += [0]*len(p_Z)
	
	# Array sizes variables initialization:
	p_n = len(p_beta)
	p_n__internal = p_n
	p_beta__internal = p_beta
	p_Z__internal = p_Z
	p_effective_charge__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_effective_charge):
		p_effective_charge__internal[i] = v
	
	ret = _libAT.lib.AT_effective_charge_from_beta(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_effective_charge__internal.encode() if type(p_effective_charge__internal) is str else p_effective_charge__internal
			)
	for i,v in enumerate(p_effective_charge__internal):
		p_effective_charge[i] = v
	
	return ret
	

def AT_energy_straggling_MeV2_cm2_g(p_E_MeV_u, p_particle_no, p_material_no, p_dsE2dz_MeV2_cm2_g):
	"""
	Wrapping function generated for C language function documented as follows:
	Get energy spread with depth according to Bohr's classical theory
	Bohr, N. (1915), Phil. Mag. 30, 581ff, see also Evans, R.D. (1955), The atomic nucleus, McGraw Hill, New York, p. 661
	In the literature dsE2dz is often given in units ergs2/cm. Here we report it mass-normalized MeV2*cm2/g
	Since the effective charge of the particle enters the equation, particle types and energies have to be given
	The equation is however limited to energies > 10 MeV/u and not too heavy ions
	TODO: add William extension for relativistic effects (Williams, E.J. (1945), Revs. Mod. Phys. 17, 217ff)
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  vector of energies of particle per nucleon [MeV/u] (array of size n)
	@param[in]  particle_no              type of the particles in the mixed particle field (array of size n)
	@param[in]  material_no              index number for slab material
	@param[out] dsE2dz_MeV2_cm2_g        Increase of energy straggling variance sigma_E^2 per unit length of material (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_dsE2dz_MeV2_cm2_g is passed correctly:
	if len(p_dsE2dz_MeV2_cm2_g) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_dsE2dz_MeV2_cm2_g was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_dsE2dz_MeV2_cm2_g.clear()
		p_dsE2dz_MeV2_cm2_g += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_dsE2dz_MeV2_cm2_g__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_dsE2dz_MeV2_cm2_g):
		p_dsE2dz_MeV2_cm2_g__internal[i] = v
	
	_libAT.lib.AT_energy_straggling_MeV2_cm2_g(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_dsE2dz_MeV2_cm2_g__internal.encode() if type(p_dsE2dz_MeV2_cm2_g__internal) is str else p_dsE2dz_MeV2_cm2_g__internal
			)
	for i,v in enumerate(p_dsE2dz_MeV2_cm2_g__internal):
		p_dsE2dz_MeV2_cm2_g[i] = v
	
	

def AT_energy_straggling_after_slab_E_MeV_u(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_m, p_initial_sigma_E_MeV_u, p_sigma_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Get energy spread of an ion beam after traversing
	a material slab according to Bohr's classical theory.
	Bohr, N. (1915), Phil. Mag. 30, 581ff, see also Evans, R.D. (1955), The atomic nucleus, McGraw Hill, New York, p. 661
	Please note that the effective charge is assumed to be constant over the material slab
	If this is not the case you should apply this routine multiple times to subslices
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  vector of energies of particle per nucleon [MeV/u] (array of size n)
	@param[in]  particle_no              type of the particles in the mixed particle field (array of size n)
	@param[in]  material_no              index number for slab material
	@param[in]  slab_thickness_m         thickness of slab in m
	@param[in]  initial_sigma_E_MeV_u    energy spread - 1 sigma - before traversing the slab - can be 0 (array of size n)
	@param[out] sigma_E_MeV_u            energy spread - 1 sigma - after traversing the slab (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_initial_sigma_E_MeV_u]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_initial_sigma_E_MeV_u]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_sigma_E_MeV_u is passed correctly:
	if len(p_sigma_E_MeV_u) != len(p_initial_sigma_E_MeV_u):
		out_array_auto_init = "\nWarning: OUT array parameter p_sigma_E_MeV_u was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_sigma_E_MeV_u.clear()
		p_sigma_E_MeV_u += [0]*len(p_initial_sigma_E_MeV_u)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_m__internal = p_slab_thickness_m
	p_initial_sigma_E_MeV_u__internal = p_initial_sigma_E_MeV_u
	p_sigma_E_MeV_u__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_sigma_E_MeV_u):
		p_sigma_E_MeV_u__internal[i] = v
	
	_libAT.lib.AT_energy_straggling_after_slab_E_MeV_u(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_m__internal.encode() if type(p_slab_thickness_m__internal) is str else p_slab_thickness_m__internal
			,p_initial_sigma_E_MeV_u__internal.encode() if type(p_initial_sigma_E_MeV_u__internal) is str else p_initial_sigma_E_MeV_u__internal
			,p_sigma_E_MeV_u__internal.encode() if type(p_sigma_E_MeV_u__internal) is str else p_sigma_E_MeV_u__internal
			)
	for i,v in enumerate(p_sigma_E_MeV_u__internal):
		p_sigma_E_MeV_u[i] = v
	
	

def AT_effective_charge_from_E_MeV_u_single(p_E_MeV_u, p_particle_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Effective charge according to Barkas-Bethe-approximation
	for particle with given energy per nucleon
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@param[in]  particle_no              type of the particles in the mixed particle field
	@return     effective_charge         Effective charge according to Barkas-Bethe-approximation
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	ret = _libAT.lib.AT_effective_charge_from_E_MeV_u_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			)
	return ret
	

def AT_effective_charge_from_E_MeV_u(p_E_MeV_u, p_particle_no, p_effective_charge):
	"""
	Wrapping function generated for C language function documented as follows:
	Effective charge according to Barkas-Bethe-approximation:
	for particles with given kinetic energy per nucleon
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  vector of energies of particle per nucleon [MeV/u] (array of size n)
	@param[in]  particle_no              type of the particles in the mixed particle field (array of size n)
	@param[out] effective_charge         Effective charge according to Barkas-Bethe-approximation (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_effective_charge is passed correctly:
	if len(p_effective_charge) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_effective_charge was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_effective_charge.clear()
		p_effective_charge += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_effective_charge__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_effective_charge):
		p_effective_charge__internal[i] = v
	
	ret = _libAT.lib.AT_effective_charge_from_E_MeV_u(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_effective_charge__internal.encode() if type(p_effective_charge__internal) is str else p_effective_charge__internal
			)
	for i,v in enumerate(p_effective_charge__internal):
		p_effective_charge[i] = v
	
	return ret
	

def AT_mean_excitation_energy_eV_from_Z_single(p_Z):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns mean excitation energy for elements (according to Sternheimer: Phys. Rev. 145, 247 in 1966)
	@param[in]  Z            		    atomic number
	@return I_eV
	"""
	p_Z__internal = p_Z
	ret = _libAT.lib.AT_mean_excitation_energy_eV_from_Z_single(p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			)
	return ret
	

def AT_mean_excitation_energy_eV_from_Z(p_Z, p_I_eV):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns mean excitation energies for elements
	@param[in]  n                        number of elements
	@param[in]  Z                   		vector of atomic numbers (array of size n)
	@param[out] I_eV        				vector of mean excitation energies (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_Z]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_I_eV is passed correctly:
	if len(p_I_eV) != len(p_Z):
		out_array_auto_init = "\nWarning: OUT array parameter p_I_eV was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_I_eV.clear()
		p_I_eV += [0]*len(p_Z)
	
	# Array sizes variables initialization:
	p_n = len(p_Z)
	p_n__internal = p_n
	p_Z__internal = p_Z
	p_I_eV__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_I_eV):
		p_I_eV__internal[i] = v
	
	ret = _libAT.lib.AT_mean_excitation_energy_eV_from_Z(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_Z__internal.encode() if type(p_Z__internal) is str else p_Z__internal
			,p_I_eV__internal.encode() if type(p_I_eV__internal) is str else p_I_eV__internal
			)
	for i,v in enumerate(p_I_eV__internal):
		p_I_eV[i] = v
	
	return ret
	

def AT_mass_correction_terms_new(p_E_MeV_u, p_A):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns mass correction terms of max relativistic energy transfer for single particle
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@param[in]  A                        atomic mass
	@return mass_correction_terms
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_A__internal = p_A
	ret = _libAT.lib.AT_mass_correction_terms_new(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			)
	return ret
	

def AT_max_relativistic_E_transfer_MeV_new_single(p_E_MeV_u, p_A):
	"""
	Wrapping function generated for C language function documented as follows:
	Max relativistic energy transfer with mass correction terms for single particle
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@param[in]  A                        atomic mass
	@return max_rel_E_transfer_MeV
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_A__internal = p_A
	ret = _libAT.lib.AT_max_relativistic_E_transfer_MeV_new_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			)
	return ret
	

def AT_max_classic_E_transfer_MeV_new_single(p_E_MeV_u, p_A):
	"""
	Wrapping function generated for C language function documented as follows:
	Max classic energy transfer for single particle
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@param[in]  A                        atomic mass
	@return max_classic_E_transfer_MeV
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_A__internal = p_A
	ret = _libAT.lib.AT_max_classic_E_transfer_MeV_new_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			)
	return ret
	

def AT_max_E_transfer_MeV_new_single(p_E_MeV_u, p_A):
	"""
	Wrapping function generated for C language function documented as follows:
	Max energy transfer for single particle
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@param[in]  A                        atomic mass
	@return     max_E_transfer_MeV
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_A__internal = p_A
	ret = _libAT.lib.AT_max_E_transfer_MeV_new_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			)
	return ret
	

def AT_max_E_transfer_MeV_new(p_E_MeV_u, p_A, p_max_E_transfer_MeV):
	"""
	Wrapping function generated for C language function documented as follows:
	Kinetic energy maximally transferred from an ion to an electron
	in a collision - relativistic or non-relativistic
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  energies of particle per nucleon [MeV/u]; if positive, the computation will be relativistic; if negative, the classic formular will be used (array of size n)
	@param[in]  A                        atomic mass (array of size n)
	@param[out] max_E_transfer_MeV       maximal energies transferred (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_A]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_A]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_max_E_transfer_MeV is passed correctly:
	if len(p_max_E_transfer_MeV) != len(p_A):
		out_array_auto_init = "\nWarning: OUT array parameter p_max_E_transfer_MeV was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_max_E_transfer_MeV.clear()
		p_max_E_transfer_MeV += [0]*len(p_A)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_A__internal = p_A
	p_max_E_transfer_MeV__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_max_E_transfer_MeV):
		p_max_E_transfer_MeV__internal[i] = v
	
	ret = _libAT.lib.AT_max_E_transfer_MeV_new(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_A__internal.encode() if type(p_A__internal) is str else p_A__internal
			,p_max_E_transfer_MeV__internal.encode() if type(p_max_E_transfer_MeV__internal) is str else p_max_E_transfer_MeV__internal
			)
	for i,v in enumerate(p_max_E_transfer_MeV__internal):
		p_max_E_transfer_MeV[i] = v
	
	return ret
	

def AT_mass_correction_terms(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns mass correction terms of max relativistic energy transfer for single particle
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@return mass_correction_terms
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_mass_correction_terms(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_max_relativistic_E_transfer_MeV_single(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Max relativistic energy transfer with mass correction terms for single particle
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@return max_rel_E_transfer_MeV
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_max_relativistic_E_transfer_MeV_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_max_classic_E_transfer_MeV_single(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Max classic energy transfer for single particle
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@return max_classic_E_transfer_MeV
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_max_classic_E_transfer_MeV_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_max_E_transfer_MeV_single(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Max energy transfer for single particle
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV/u]
	@return     max_E_transfer_MeV
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_max_E_transfer_MeV_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_max_E_transfer_MeV(p_E_MeV_u, p_max_E_transfer_MeV):
	"""
	Wrapping function generated for C language function documented as follows:
	Kinetic energy maximally transferred from an ion to an electron
	in a collision - relativistic or non-relativistic
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  energies of particle per nucleon [MeV/u]; if positive, the computation will be relativistic; if negative, the classic formular will be used (array of size n)
	@param[out] max_E_transfer_MeV       maximal energies transferred (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_max_E_transfer_MeV is passed correctly:
	if len(p_max_E_transfer_MeV) != len(p_E_MeV_u):
		out_array_auto_init = "\nWarning: OUT array parameter p_max_E_transfer_MeV was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_max_E_transfer_MeV.clear()
		p_max_E_transfer_MeV += [0]*len(p_E_MeV_u)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_max_E_transfer_MeV__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_max_E_transfer_MeV):
		p_max_E_transfer_MeV__internal[i] = v
	
	ret = _libAT.lib.AT_max_E_transfer_MeV(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_max_E_transfer_MeV__internal.encode() if type(p_max_E_transfer_MeV__internal) is str else p_max_E_transfer_MeV__internal
			)
	for i,v in enumerate(p_max_E_transfer_MeV__internal):
		p_max_E_transfer_MeV[i] = v
	
	return ret
	

def AT_momentum_from_E_MeV_c_u_single(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns relativistic momentum (per nucleon) of particle
	@param[in]	  	E_MeV_u             kinetic Energy per nucleon [MeV/u]
	@return                              momentum [MeV/c]
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_momentum_from_E_MeV_c_u_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_momentum_MeV_c_u_from_E_MeV_u(p_E_MeV_u, p_momentum_MeV_c):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns relativistic momenta per nucleon for particles with given kinetic energy
	@param[in]	n						number of particles
	@param[in]  	E_MeV_u                 kinetic energy per nucleon [MeV/u] (array of size n)
	@param[out]	momentum_MeV_c  		momentum per nucleon (array of size n)
	@return                              return code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_momentum_MeV_c is passed correctly:
	if len(p_momentum_MeV_c) != len(p_E_MeV_u):
		out_array_auto_init = "\nWarning: OUT array parameter p_momentum_MeV_c was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_momentum_MeV_c.clear()
		p_momentum_MeV_c += [0]*len(p_E_MeV_u)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_momentum_MeV_c__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_momentum_MeV_c):
		p_momentum_MeV_c__internal[i] = v
	
	ret = _libAT.lib.AT_momentum_MeV_c_u_from_E_MeV_u(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_momentum_MeV_c__internal.encode() if type(p_momentum_MeV_c__internal) is str else p_momentum_MeV_c__internal
			)
	for i,v in enumerate(p_momentum_MeV_c__internal):
		p_momentum_MeV_c[i] = v
	
	return ret
	

def AT_dose_Gy_from_fluence_cm2_single(p_E_MeV_u, p_particle_no, p_fluence_cm2, p_material_no, p_stopping_power_source_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns dose in Gy for particle with given fluence and energy
	@param[in]  E_MeV_u      energy per unit mass [MeV/u]
	@param[in]  particle_no  type of the particle
	@see          AT_DataParticle.h for definition
	@param[in]  fluence_cm2  fluence in 1/cm2
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  stopping_power_source_no  stopping power source index
	@return     D_Gy         dose in Gy
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2__internal = p_fluence_cm2
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	ret = _libAT.lib.AT_dose_Gy_from_fluence_cm2_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			)
	return ret
	

def AT_dose_Gy_from_fluence_cm2(p_E_MeV_u, p_particle_no, p_fluence_cm2, p_material_no, p_stopping_power_source_no, p_dose_Gy):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns dose in Gy for each given particle
	@param[in]  n            number of particle types in the mixed particle field
	@param[in]  E_MeV_u      energy of particles in the mixed particle field [MeV/u] (array of size n)
	@param[in]  particle_no  type of the particles in the mixed particle field (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]  fluence_cm2  fluence for each particle type (array of size n)
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  stopping_power_source_no  stopping power source index
	@param[out] dose_Gy          be allocated by the user which will be used to return the results (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_dose_Gy is passed correctly:
	if len(p_dose_Gy) != len(p_fluence_cm2):
		out_array_auto_init = "\nWarning: OUT array parameter p_dose_Gy was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_dose_Gy.clear()
		p_dose_Gy += [0]*len(p_fluence_cm2)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2__internal = p_fluence_cm2
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_dose_Gy__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_dose_Gy):
		p_dose_Gy__internal[i] = v
	
	_libAT.lib.AT_dose_Gy_from_fluence_cm2(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_dose_Gy__internal.encode() if type(p_dose_Gy__internal) is str else p_dose_Gy__internal
			)
	for i,v in enumerate(p_dose_Gy__internal):
		p_dose_Gy[i] = v
	
	

def AT_fluence_cm2_from_dose_Gy_single(p_E_MeV_u, p_particle_no, p_D_Gy, p_material_no, p_stopping_power_source_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns fluence in 1/cm2 for particles with given dose and energy
	@param[in]  E_MeV_u      energy of particle per nucleon [MeV/u]
	@param[in]  particle_no  type of the particles
	@see          AT_DataParticle.h for definition
	@param[in]  D_Gy         dose in Gy
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  stopping_power_source_no  TODO
	@return fluence in 1/cm2
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_D_Gy__internal = p_D_Gy
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	ret = _libAT.lib.AT_fluence_cm2_from_dose_Gy_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_D_Gy__internal.encode() if type(p_D_Gy__internal) is str else p_D_Gy__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			)
	return ret
	

def AT_fluence_cm2_from_dose_Gy(p_E_MeV_u, p_particle_no, p_D_Gy, p_material_no, p_stopping_power_source_no, p_fluence_cm2):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns fluence in 1/cm2 for each given particle
	@param[in]  n            number of particle types in the mixed particle field
	@param[in]  E_MeV_u      energy per nucleon of particles in the mixed particle field [MeV/u] (array of size n)
	@param[in]  particle_no  type of the particles in the mixed particle field (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]  D_Gy         dose / Gy for each particle type (array of size n)
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  stopping_power_source_no  TODO
	@param[out] fluence_cm2         to be allocated by the user which will be used to return the results (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_D_Gy]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_D_Gy]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_fluence_cm2 is passed correctly:
	if len(p_fluence_cm2) != len(p_D_Gy):
		out_array_auto_init = "\nWarning: OUT array parameter p_fluence_cm2 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_fluence_cm2.clear()
		p_fluence_cm2 += [0]*len(p_D_Gy)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_D_Gy__internal = p_D_Gy
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_fluence_cm2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_fluence_cm2):
		p_fluence_cm2__internal[i] = v
	
	_libAT.lib.AT_fluence_cm2_from_dose_Gy(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_D_Gy__internal.encode() if type(p_D_Gy__internal) is str else p_D_Gy__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			)
	for i,v in enumerate(p_fluence_cm2__internal):
		p_fluence_cm2[i] = v
	
	

def AT_beam_par_physical_to_technical(p_fluence_cm2, p_sigma_cm, p_N, p_FWHM_mm):
	"""
	Wrapping function generated for C language function documented as follows:
	Converts physical beam parameters of a symmetric, double lateral Gaussian shape beam, i.e.
	central (=peak) fluence and width (= 1 standard deviation)
	to technical, accelerator parameters, i.e.
	total number of particles and FWHM
	@param[in]      n             length of vectors for parameters
	@param[in]      fluence_cm2   fluence in beam center (array of size n)
	@param[in]      sigma_cm      beam width stdev (array of size n)
	@param[out]     N             resulting absolute particle numbers (array of size n)
	@param[out]     FWHM_mm       resulting FWHMs (in mm) (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_fluence_cm2,p_sigma_cm]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_fluence_cm2)
	for in_array_argument in [p_fluence_cm2,p_sigma_cm]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_N is passed correctly:
	if len(p_N) != len(p_sigma_cm):
		out_array_auto_init = "\nWarning: OUT array parameter p_N was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_N.clear()
		p_N += [0]*len(p_sigma_cm)
	
	# Procedure to check if OUT array p_FWHM_mm is passed correctly:
	if len(p_FWHM_mm) != len(p_sigma_cm):
		out_array_auto_init = "\nWarning: OUT array parameter p_FWHM_mm was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_FWHM_mm.clear()
		p_FWHM_mm += [0]*len(p_sigma_cm)
	
	# Array sizes variables initialization:
	p_n = len(p_fluence_cm2)
	p_n__internal = p_n
	p_fluence_cm2__internal = p_fluence_cm2
	p_sigma_cm__internal = p_sigma_cm
	p_N__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_N):
		p_N__internal[i] = v
	
	p_FWHM_mm__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_FWHM_mm):
		p_FWHM_mm__internal[i] = v
	
	_libAT.lib.AT_beam_par_physical_to_technical(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_sigma_cm__internal.encode() if type(p_sigma_cm__internal) is str else p_sigma_cm__internal
			,p_N__internal.encode() if type(p_N__internal) is str else p_N__internal
			,p_FWHM_mm__internal.encode() if type(p_FWHM_mm__internal) is str else p_FWHM_mm__internal
			)
	for i,v in enumerate(p_N__internal):
		p_N[i] = v
	
	for i,v in enumerate(p_FWHM_mm__internal):
		p_FWHM_mm[i] = v
	
	

def AT_beam_par_technical_to_physical(p_N, p_FWHM_mm, p_fluence_cm2, p_sigma_cm):
	"""
	Wrapping function generated for C language function documented as follows:
	Converts technical, accelerator parameters of a symmetric, double lateral Gaussian shape beam, i.e.
	total number of particles and FWHM to
	physical beam parameters, i.e.
	central (=peak) fluence and width (= 1 standard deviation)
	@param[in]      n             length of vectors for parameters
	@param[in]      N             absolute particle numbers (array of size n)
	@param[in]      FWHM_mm       FWHMs (in mm) (array of size n)
	@param[out]     fluence_cm2   resulting fluence in beam center (array of size n)
	@param[out]     sigma_cm      resulting beam width stdev (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_N,p_FWHM_mm]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_N)
	for in_array_argument in [p_N,p_FWHM_mm]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_fluence_cm2 is passed correctly:
	if len(p_fluence_cm2) != len(p_FWHM_mm):
		out_array_auto_init = "\nWarning: OUT array parameter p_fluence_cm2 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_fluence_cm2.clear()
		p_fluence_cm2 += [0]*len(p_FWHM_mm)
	
	# Procedure to check if OUT array p_sigma_cm is passed correctly:
	if len(p_sigma_cm) != len(p_FWHM_mm):
		out_array_auto_init = "\nWarning: OUT array parameter p_sigma_cm was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_sigma_cm.clear()
		p_sigma_cm += [0]*len(p_FWHM_mm)
	
	# Array sizes variables initialization:
	p_n = len(p_N)
	p_n__internal = p_n
	p_N__internal = p_N
	p_FWHM_mm__internal = p_FWHM_mm
	p_fluence_cm2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_fluence_cm2):
		p_fluence_cm2__internal[i] = v
	
	p_sigma_cm__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_sigma_cm):
		p_sigma_cm__internal[i] = v
	
	_libAT.lib.AT_beam_par_technical_to_physical(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_N__internal.encode() if type(p_N__internal) is str else p_N__internal
			,p_FWHM_mm__internal.encode() if type(p_FWHM_mm__internal) is str else p_FWHM_mm__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_sigma_cm__internal.encode() if type(p_sigma_cm__internal) is str else p_sigma_cm__internal
			)
	for i,v in enumerate(p_fluence_cm2__internal):
		p_fluence_cm2[i] = v
	
	for i,v in enumerate(p_sigma_cm__internal):
		p_sigma_cm[i] = v
	
	

def AT_interparticleDistance_m(p_LET_MeV_cm2_g, p_fluence_cm2, p_results_m):
	"""
	Wrapping function generated for C language function documented as follows:
	Interparticle distance
	@param[in]      n               length of vectors for parameters
	@param[in]      LET_MeV_cm2_g   LET for each particle type (array of size n)
	@param[in]      fluence_cm2     fluence for each particle type (array of size n)
	@param[out]     results_m       interparticle distance for each particle type (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_LET_MeV_cm2_g,p_fluence_cm2]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_LET_MeV_cm2_g)
	for in_array_argument in [p_LET_MeV_cm2_g,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_results_m is passed correctly:
	if len(p_results_m) != len(p_fluence_cm2):
		out_array_auto_init = "\nWarning: OUT array parameter p_results_m was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_results_m.clear()
		p_results_m += [0]*len(p_fluence_cm2)
	
	# Array sizes variables initialization:
	p_n = len(p_LET_MeV_cm2_g)
	p_n__internal = p_n
	p_LET_MeV_cm2_g__internal = p_LET_MeV_cm2_g
	p_fluence_cm2__internal = p_fluence_cm2
	p_results_m__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_results_m):
		p_results_m__internal[i] = v
	
	_libAT.lib.AT_interparticleDistance_m(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_LET_MeV_cm2_g__internal.encode() if type(p_LET_MeV_cm2_g__internal) is str else p_LET_MeV_cm2_g__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_results_m__internal.encode() if type(p_results_m__internal) is str else p_results_m__internal
			)
	for i,v in enumerate(p_results_m__internal):
		p_results_m[i] = v
	
	

def AT_inv_interparticleDistance_Gy(p_LET_MeV_cm2_g, p_distance_m, p_results_Gy):
	"""
	Wrapping function generated for C language function documented as follows:
	Inverse interparticle distance
	@param[in]      n               length of vectors for parameters
	@param[in]      LET_MeV_cm2_g   LET for each particle type (array of size n)
	@param[in]      distance_m      interparticle distance for each particle type (array of size n)
	@param[out]     results_Gy
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_LET_MeV_cm2_g,p_distance_m]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_LET_MeV_cm2_g)
	for in_array_argument in [p_LET_MeV_cm2_g,p_distance_m]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_results_Gy, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_results_Gy) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_results_Gy.clear()
		p_results_Gy += [0]
	
	# Array sizes variables initialization:
	p_n = len(p_LET_MeV_cm2_g)
	p_n__internal = p_n
	p_LET_MeV_cm2_g__internal = p_LET_MeV_cm2_g
	p_distance_m__internal = p_distance_m
	p_results_Gy__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_results_Gy):
		p_results_Gy__internal[i] = v
	
	_libAT.lib.AT_inv_interparticleDistance_Gy(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_LET_MeV_cm2_g__internal.encode() if type(p_LET_MeV_cm2_g__internal) is str else p_LET_MeV_cm2_g__internal
			,p_distance_m__internal.encode() if type(p_distance_m__internal) is str else p_distance_m__internal
			,p_results_Gy__internal.encode() if type(p_results_Gy__internal) is str else p_results_Gy__internal
			)
	for i,v in enumerate(p_results_Gy__internal):
		p_results_Gy[i] = v
	
	

def AT_single_impact_fluence_cm2_single(p_E_MeV_u, p_material_no, p_er_model):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the fluences at which (for a given material and electron-range model) every
	point of the detector lies within the area ONE track only
	Needed by SuccessiveConvolutions
	@param[in]  E_MeV_u      energy of particle per nucleon [MeV/u]
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  er_model     index of electron-range model
	@see          AT_ElectronRange.h for definition
	@return     single_impact_fluence_cm2  results (one for each entry in the parameter vectors)
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_material_no__internal = p_material_no
	p_er_model__internal = p_er_model
	ret = _libAT.lib.AT_single_impact_fluence_cm2_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			)
	return ret
	

def AT_single_impact_fluence_cm2(p_E_MeV_u, p_material_no, p_er_model, p_single_impact_fluence_cm2):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the fluences at which (for a given material and electron-range model) every
	point of the detector lies within the area ONE track only
	Needed by SuccessiveConvolutions
	@param[in]  n            length of vectors for parameters
	@param[in]  E_MeV_u      energy per nucleon of particles in the mixed particle field [MeV/u] (array of size n)
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  er_model     index of electron-range model
	@see          AT_ElectronRange.h for definition
	@param[out] single_impact_fluence_cm2  results (one for each entry in the parameter vectors) (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_single_impact_fluence_cm2 is passed correctly:
	if len(p_single_impact_fluence_cm2) != len(p_E_MeV_u):
		out_array_auto_init = "\nWarning: OUT array parameter p_single_impact_fluence_cm2 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_single_impact_fluence_cm2.clear()
		p_single_impact_fluence_cm2 += [0]*len(p_E_MeV_u)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_material_no__internal = p_material_no
	p_er_model__internal = p_er_model
	p_single_impact_fluence_cm2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_single_impact_fluence_cm2):
		p_single_impact_fluence_cm2__internal[i] = v
	
	_libAT.lib.AT_single_impact_fluence_cm2(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_single_impact_fluence_cm2__internal.encode() if type(p_single_impact_fluence_cm2__internal) is str else p_single_impact_fluence_cm2__internal
			)
	for i,v in enumerate(p_single_impact_fluence_cm2__internal):
		p_single_impact_fluence_cm2[i] = v
	
	

def AT_single_impact_dose_Gy_single(p_LET_MeV_cm2_g, p_single_impact_fluence_cm2):
	"""
	Wrapping function generated for C language function documented as follows:
	Dose for the fluence at a single impact
	@param[in] LET_MeV_cm2_g              LET of particle
	@param[in] single_impact_fluence_cm2  the fluence corresponding to a single impact
	@return    single impact dose
	"""
	p_LET_MeV_cm2_g__internal = p_LET_MeV_cm2_g
	p_single_impact_fluence_cm2__internal = p_single_impact_fluence_cm2
	ret = _libAT.lib.AT_single_impact_dose_Gy_single(p_LET_MeV_cm2_g__internal.encode() if type(p_LET_MeV_cm2_g__internal) is str else p_LET_MeV_cm2_g__internal
			,p_single_impact_fluence_cm2__internal.encode() if type(p_single_impact_fluence_cm2__internal) is str else p_single_impact_fluence_cm2__internal
			)
	return ret
	

def AT_single_impact_dose_Gy(p_E_MeV_u, p_particle_no, p_material_no, p_er_model, p_stopping_power_source_no, p_single_impact_dose_Gy):
	"""
	Wrapping function generated for C language function documented as follows:
	Doses for the fluences at a single impact
	@param[in]  n                          number of particles
	@param[in]  E_MeV_u                    energy per nucleon [MeV/u] (array of size n)
	@param[in]  particle_no                particle type (array of size n)
	@param[in]  material_no                material
	@param[in]  er_model                   electron-range model
	@param[in]  stopping_power_source_no   TODO
	@param[out] single_impact_dose_Gy      resulting single impact doses (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_single_impact_dose_Gy is passed correctly:
	if len(p_single_impact_dose_Gy) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_single_impact_dose_Gy was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_single_impact_dose_Gy.clear()
		p_single_impact_dose_Gy += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_er_model__internal = p_er_model
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_single_impact_dose_Gy__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_single_impact_dose_Gy):
		p_single_impact_dose_Gy__internal[i] = v
	
	_libAT.lib.AT_single_impact_dose_Gy(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_single_impact_dose_Gy__internal.encode() if type(p_single_impact_dose_Gy__internal) is str else p_single_impact_dose_Gy__internal
			)
	for i,v in enumerate(p_single_impact_dose_Gy__internal):
		p_single_impact_dose_Gy[i] = v
	
	

def AT_total_D_Gy(p_E_MeV_u, p_particle_no, p_fluence_cm2, p_material_no, p_stopping_power_source_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the total dose of a mixed particle field
	@param[in]  number_of_field_components            number of components in the mixed field
	@param[in]  E_MeV_u                               energy of particles in the mixed particle field [MeV/u] (array of size number_of_field_components)
	@param[in]  particle_no                           particle index (array of size number_of_field_components)
	@see AT_DataParticle.h for definition
	@param[in]  fluence_cm2                           fluences of particles in the mixed particle field (array of size number_of_field_components)
	@param[in]  material_no                           material index
	@see AT_DataMaterial.h for definition
	@param[in]  stopping_power_source_no              TODO
	@return     total_dose_Gy                         result
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2__internal = p_fluence_cm2
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	ret = _libAT.lib.AT_total_D_Gy(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			)
	return ret
	

def AT_total_fluence_cm2(p_E_MeV_u, p_particle_no, p_D_Gy, p_material_no, p_stopping_power_source_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the total fluence of a mixed particle field
	@param[in]  number_of_field_components            number of components in the mixed field
	@param[in]  E_MeV_u                               energy of particles in the mixed particle field [MeV/u] (array of size number_of_field_components)
	@param[in]  particle_no                           particle index (array of size number_of_field_components)
	@see AT_DataParticle.h for definition
	@param[in]  D_Gy                                  doses of particles in the mixed particle field (array of size number_of_field_components)
	@param[in]  material_no                           material index
	@param[in]  stopping_power_source_no              TODO
	@see AT_DataMaterial.h for definition
	@return     total_fluence_cm                      result
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_D_Gy]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_D_Gy]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_D_Gy__internal = p_D_Gy
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	ret = _libAT.lib.AT_total_fluence_cm2(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_D_Gy__internal.encode() if type(p_D_Gy__internal) is str else p_D_Gy__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			)
	return ret
	

def AT_fluence_weighted_E_MeV_u(p_E_MeV_u, p_fluence_cm2):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the fluence-weighted average energy of a particle field
	Needed by SuccessiveConvolutions
	@param[in]  number_of_field_components            number of components in mixed particle field
	@param[in]  E_MeV_u      energy of particles in the mixed particle field [MeV/u] (array of size number_of_field_components)
	@param[in]  fluence_cm2  fluences of particles in the mixed particle field (array of size number_of_field_components)
	@return     average_E_MeV_u  fluence-weighted mean energy
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_fluence_cm2]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_fluence_cm2__internal = p_fluence_cm2
	ret = _libAT.lib.AT_fluence_weighted_E_MeV_u(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			)
	return ret
	

def AT_dose_weighted_E_MeV_u(p_E_MeV_u, p_particle_no, p_fluence_cm2, p_material_no, p_stopping_power_source_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the dose-weighted average energy of a particle field
	Needed by SuccessiveConvolutions
	@param[in]  number_of_field_components            number of components in mixed particle field
	@param[in]  E_MeV_u      energy of particles in the mixed particle field [MeV/u] (array of size number_of_field_components)
	@param[in]  particle_no  particle index (array of size number_of_field_components)
	@see          AT_DataParticle.h for definition
	@param[in]  fluence_cm2  fluences of particles in the mixed particle field (array of size number_of_field_components)
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  stopping_power_source_no  TODO
	@return     dose-weighted mean energy
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2__internal = p_fluence_cm2
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	ret = _libAT.lib.AT_dose_weighted_E_MeV_u(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			)
	return ret
	

def AT_fluence_weighted_LET_MeV_cm2_g(p_E_MeV_u, p_particle_no, p_fluence_cm2, p_material_no, p_stopping_power_source_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the fluence-weighted average LET of a particle field
	@param[in]  number_of_field_components            number of components in mixed particle field
	@param[in]  E_MeV_u      energy of particles in the mixed particle field [MeV/u] (array of size number_of_field_components)
	@param[in]  particle_no  particle index (array of size number_of_field_components)
	@see          AT_DataParticle.h for definition
	@param[in]  fluence_cm2  fluences of particles in the mixed particle field (array of size number_of_field_components)
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  stopping_power_source_no  TODO
	@return     fluence-weighted LET
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2__internal = p_fluence_cm2
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	ret = _libAT.lib.AT_fluence_weighted_LET_MeV_cm2_g(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			)
	return ret
	

def AT_dose_weighted_LET_MeV_cm2_g(p_E_MeV_u, p_particle_no, p_fluence_cm2, p_material_no, p_stopping_power_source_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the dose-weighted average LET of a particle field
	@param[in]  number_of_field_components            number of components in mixed particle field
	@param[in]  E_MeV_u      energy of particles in the mixed particle field [MeV/u] (array of size number_of_field_components)
	@param[in]  particle_no  particle index (array of size number_of_field_components)
	@see          AT_DataParticle.h for definition
	@param[in]  fluence_cm2  fluences of particles in the mixed particle field (array of size number_of_field_components)
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  stopping_power_source_no  TODO
	@return     dose-weighted LET
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2__internal = p_fluence_cm2
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	ret = _libAT.lib.AT_dose_weighted_LET_MeV_cm2_g(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			)
	return ret
	

def AT_stopping_power_ratio(p_E_MeV_u, p_particle_no, p_fluence_cm2, p_material_no, p_reference_material_no, p_stopping_power_source_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the stopping power ratio for a material and a reference material.
	In case of mixed particle fields, the stopping power ratios of individual components are
	weighted by their respective fluences. Thus, this routines computes the ration of fluence-weighted
	stopping powers, NOT of dose-weighted stopping powers.
	@param[in]  number_of_field_components            number of components in mixed field
	@param[in]  E_MeV_u      energy of particles in the mixed particle field [MeV/u] (array of size number_of_field_components)
	@param[in]  particle_no  particle index (array of size number_of_field_components)
	@see          AT_DataParticle.h for definition
	@param[in]  fluence_cm2  fluences of particles in the mixed particle field (array of size number_of_field_components)
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  reference_material_no  material index of reference material
	@param[in]  stopping_power_source_no  TODO
	@return     stopping power ratio
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2__internal = p_fluence_cm2
	p_material_no__internal = p_material_no
	p_reference_material_no__internal = p_reference_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	ret = _libAT.lib.AT_stopping_power_ratio(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_reference_material_no__internal.encode() if type(p_reference_material_no__internal) is str else p_reference_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			)
	return ret
	

def AT_mean_number_of_tracks_contrib(p_E_MeV_u, p_particle_no, p_fluence_cm2, p_material_no, p_er_model, p_stopping_power_source_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the number of track contributing to a representative point in a mixed field
	@param[in]  number_of_field_components            number of components in mixed particle field
	@param[in]  E_MeV_u      energy of particles in the mixed particle field [MeV/u] (array of size number_of_field_components)
	@param[in]  particle_no  particle index (array of size number_of_field_components)
	@see          AT_DataParticle.h for definition
	@param[in]  fluence_cm2  fluences of particles in the mixed particle field (array of size number_of_field_components)
	@param[in]  material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]  er_model     chosen electron-range-model
	@param[in]  stopping_power_source_no     TODO
	@return     resulting mean number of tracks contributing
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2__internal = p_fluence_cm2
	p_material_no__internal = p_material_no
	p_er_model__internal = p_er_model
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	ret = _libAT.lib.AT_mean_number_of_tracks_contrib(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			)
	return ret
	

def AT_kinetic_variable_single(p_E_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the kinetic variable needed for computation of
	density effect in Bethe formula for stopping power
	following the Sternheimer (1971) approach
	@param[in]  E_MeV_u      energy per nucleon of particle [MeV]
	@return     				kinetic variable
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	ret = _libAT.lib.AT_kinetic_variable_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			)
	return ret
	

def AT_Rutherford_SDCS(p_E_MeV_u, p_particle_no, p_material_no, p_T_MeV, p_dsdT_m2_MeV):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the Rutherford single differential cross section
	for the energy spectrum of secondary electrons produced by
	an HCP
	@param[in]  	   E_MeV_u      energy of particle per nucleon [MeV/u]
	@param[in]  	   particle_no  particle index
	@param[in]      material_no  material index
	@param[in]  	   n      		number of secondary electron energies
	@param[in]      T_MeV 	    electron energies (array of size n)
	@param[out]     dsdT_m2_MeV  Rutherford SDCS for given electron energies (array of size n)
	@return         status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_T_MeV]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_dsdT_m2_MeV is passed correctly:
	if len(p_dsdT_m2_MeV) != len(p_T_MeV):
		out_array_auto_init = "\nWarning: OUT array parameter p_dsdT_m2_MeV was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_dsdT_m2_MeV.clear()
		p_dsdT_m2_MeV += [0]*len(p_T_MeV)
	
	# Array sizes variables initialization:
	p_n = len(p_T_MeV)
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_n__internal = p_n
	p_T_MeV__internal = p_T_MeV
	p_dsdT_m2_MeV__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_dsdT_m2_MeV):
		p_dsdT_m2_MeV__internal[i] = v
	
	ret = _libAT.lib.AT_Rutherford_SDCS(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_T_MeV__internal.encode() if type(p_T_MeV__internal) is str else p_T_MeV__internal
			,p_dsdT_m2_MeV__internal.encode() if type(p_dsdT_m2_MeV__internal) is str else p_dsdT_m2_MeV__internal
			)
	for i,v in enumerate(p_dsdT_m2_MeV__internal):
		p_dsdT_m2_MeV[i] = v
	
	return ret
	

def AT_Rutherford_scatter_cross_section(p_E_MeV_u, p_particle_no, p_material_no, p_scattering_angle, p_scatter_cross_section):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the cross section (in 1/m2) the a particle is scattered
	in the solid angle O = 2 * pi * theta * d_theta given the
	scatter angle theta
	@param[in]  E_MeV_u      			energy of incoming particle per nucleon [MeV/u]
	@param[in]  particle_no  			particle index
	@see          AT_DataParticle.h for definition
	@param[in]  material_no  			material index
	@see          AT_DataMaterial.h for definition
	@param[in]  n						number of scattering angles given
	@param[in]  scattering_angle			scattering angles theta (array of size n)
	@param[out] scatter_cross_section	scatter cross section (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_scattering_angle]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_scatter_cross_section is passed correctly:
	if len(p_scatter_cross_section) != len(p_scattering_angle):
		out_array_auto_init = "\nWarning: OUT array parameter p_scatter_cross_section was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_scatter_cross_section.clear()
		p_scatter_cross_section += [0]*len(p_scattering_angle)
	
	# Array sizes variables initialization:
	p_n = len(p_scattering_angle)
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_n__internal = p_n
	p_scattering_angle__internal = p_scattering_angle
	p_scatter_cross_section__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_scatter_cross_section):
		p_scatter_cross_section__internal[i] = v
	
	ret = _libAT.lib.AT_Rutherford_scatter_cross_section(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_scattering_angle__internal.encode() if type(p_scattering_angle__internal) is str else p_scattering_angle__internal
			,p_scatter_cross_section__internal.encode() if type(p_scatter_cross_section__internal) is str else p_scatter_cross_section__internal
			)
	for i,v in enumerate(p_scatter_cross_section__internal):
		p_scatter_cross_section[i] = v
	
	return ret
	

def AT_gyroradius_m(p_E_MeV_u, p_particle_no, p_B_T):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the gyroradius for a particle in a magnetic field. For this,
	the effective charge of the particle (as a function of the kinetic energy)
	is used.
	@param[in]  E_MeV_u      			energy of incoming particle per nucleon [MeV/u]
	@param[in]  particle_no  			particle index
	@see          AT_DataParticle.h for definition
	@param[in]  B_T						magnetic B-field strength in Tesla
	@return     gyroradius in m
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_B_T__internal = p_B_T
	ret = _libAT.lib.AT_gyroradius_m(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_B_T__internal.encode() if type(p_B_T__internal) is str else p_B_T__internal
			)
	return ret
	

def AT_Mass_Stopping_Power(p_stopping_power_source, p_E_MeV_u, p_particle_no, p_material_no, p_stopping_power_MeV_cm2_g):
	"""
	Wrapping function generated for C language function documented as follows:
	@brief Main routines for stopping power data
	Retrieves the electronic mass stopping power in MeV*cm2/g
	for the requested energies and particles for a specified
	material and data source. The data source is thereby
	given via its name (s. AT_StoppingPowerData.h from
	details), except for data that should be read for
	a file, in this case the (path and) filename has to be
	provided. In this case, the user has to make sure that
	energy and stopping power units are correct and that
	the data match the given material (use material.no = 0
	for custom-defined material).
	The file has to be plain
	ASCII with three columns (separated by space)
	charge, energy, and stopping power
	and sorted in ascending order by first charge than energy
	any alphanumeric comment can be inserted (in separate
	lines)
	@param[in]      stopping_power_source       name of the data source
	@param[in]      n		               number of energies / particles
	@param[in]      E_MeV_u                     kinetic energies in MeV per amu (array of size n)
	@param[in]      particle_no                 particle numbers (array of size n)
	@param[in]      material_no                 material number
	@param[out]     stopping_power_MeV_cm2_g    array to return stopping powers (array of size n)
	@return         status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_stopping_power_MeV_cm2_g is passed correctly:
	if len(p_stopping_power_MeV_cm2_g) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_stopping_power_MeV_cm2_g was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_stopping_power_MeV_cm2_g.clear()
		p_stopping_power_MeV_cm2_g += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_stopping_power_source__internal = p_stopping_power_source
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_stopping_power_MeV_cm2_g__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_stopping_power_MeV_cm2_g):
		p_stopping_power_MeV_cm2_g__internal[i] = v
	
	ret = _libAT.lib.AT_Mass_Stopping_Power(p_stopping_power_source__internal.encode() if type(p_stopping_power_source__internal) is str else p_stopping_power_source__internal
			,p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_MeV_cm2_g__internal.encode() if type(p_stopping_power_MeV_cm2_g__internal) is str else p_stopping_power_MeV_cm2_g__internal
			)
	for i,v in enumerate(p_stopping_power_MeV_cm2_g__internal):
		p_stopping_power_MeV_cm2_g[i] = v
	
	return ret
	

def AT_Stopping_Power(p_stopping_power_source, p_E_MeV_u, p_particle_no, p_material_no, p_stopping_power_keV_um):
	"""
	Wrapping function generated for C language function documented as follows:
	Retrieves the electronic stopping power in keV/um for
	the requested energies and particles for a specified
	material and data source. The data source is thereby
	given via its name (s. AT_StoppingPowerData.h for
	details), except for data that should be read from
	a file, in this case the (path and) filename has to be
	provided. In this case, the user has to make sure that
	energy and stopping power units are correct and that
	the data match the given material (use material.no = 0
	for custom-defined material) for density scaling.
	
	The file has to be plain
	ASCII with three columns (separated by space)
	charge, energy, and stopping power
	and sorted in ascending order by first charge than energy
	any alphanumeric comment can be inserted (in separate
	lines)
	@param[in]   stopping_power_source		name of the data source
	@param[in]   n							number of energies / particles
	@param[in]   E_MeV_u						kinetic energies in MeV per amu (array of size n)
	@param[in]   particle_no                 particle numbers (array of size n)
	@param[in]   material_no                 material number
	@param[out]  stopping_power_keV_um       array to return stopping powers (array of size n)
	@return		status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_stopping_power_keV_um is passed correctly:
	if len(p_stopping_power_keV_um) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_stopping_power_keV_um was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_stopping_power_keV_um.clear()
		p_stopping_power_keV_um += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_stopping_power_source__internal = p_stopping_power_source
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_stopping_power_keV_um__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_stopping_power_keV_um):
		p_stopping_power_keV_um__internal[i] = v
	
	ret = _libAT.lib.AT_Stopping_Power(p_stopping_power_source__internal.encode() if type(p_stopping_power_source__internal) is str else p_stopping_power_source__internal
			,p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_keV_um__internal.encode() if type(p_stopping_power_keV_um__internal) is str else p_stopping_power_keV_um__internal
			)
	for i,v in enumerate(p_stopping_power_keV_um__internal):
		p_stopping_power_keV_um[i] = v
	
	return ret
	

def AT_Mass_Stopping_Power_with_no(p_stopping_power_source_no, p_E_MeV_u, p_particle_no, p_material_no, p_stopping_power_MeV_cm2_g):
	"""
	Wrapping function generated for C language function documented as follows:
	Retrieves the electronic mass stopping power in MeV*cm2/g
	for the requested energies and particles for a specified
	material and data source. The data source is thereby
	given via its integer id (s. AT_StoppingPowerData.h for
	details). Data that should be read from a file
	cannot be used with this method.
	@param[in]   stopping_power_source_no	id of the data source
	@param[in]   n							number of energies / particles
	@param[in]   E_MeV_u						kinetic energies in MeV per amu (array of size n)
	@param[in]   particle_no                 particle numbers (array of size n)
	@param[in]   material_no                 material number
	@param[out]  stopping_power_MeV_cm2_g    array to return stopping powers (array of size n)
	@return		status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_stopping_power_MeV_cm2_g is passed correctly:
	if len(p_stopping_power_MeV_cm2_g) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_stopping_power_MeV_cm2_g was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_stopping_power_MeV_cm2_g.clear()
		p_stopping_power_MeV_cm2_g += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_stopping_power_MeV_cm2_g__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_stopping_power_MeV_cm2_g):
		p_stopping_power_MeV_cm2_g__internal[i] = v
	
	ret = _libAT.lib.AT_Mass_Stopping_Power_with_no(p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_MeV_cm2_g__internal.encode() if type(p_stopping_power_MeV_cm2_g__internal) is str else p_stopping_power_MeV_cm2_g__internal
			)
	for i,v in enumerate(p_stopping_power_MeV_cm2_g__internal):
		p_stopping_power_MeV_cm2_g[i] = v
	
	return ret
	

def AT_Stopping_Power_with_no(p_stopping_power_source_no, p_E_MeV_u, p_particle_no, p_material_no, p_stopping_power_keV_um):
	"""
	Wrapping function generated for C language function documented as follows:
	Retrieves the electronic stopping power in keV/um for
	the requested energies and particles for a specified
	material and data source. The data source is thereby
	given via its integer id (s. AT_StoppingPowerData.h for
	details). Data that should be read from a file
	cannot be used with this method.
	@param[in]   stopping_power_source_no	id of the data source
	@param[in]   n							number of energies / particles
	@param[in]   E_MeV_u						kinetic energies in MeV per amu (array of size n)
	@param[in]   particle_no                 particle numbers (array of size n)
	@param[in]   material_no                 material number
	@param[out]  stopping_power_keV_um       array to return stopping powers (array of size n)
	@return		status
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_stopping_power_keV_um is passed correctly:
	if len(p_stopping_power_keV_um) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_stopping_power_keV_um was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_stopping_power_keV_um.clear()
		p_stopping_power_keV_um += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_stopping_power_keV_um__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_stopping_power_keV_um):
		p_stopping_power_keV_um__internal[i] = v
	
	ret = _libAT.lib.AT_Stopping_Power_with_no(p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_keV_um__internal.encode() if type(p_stopping_power_keV_um__internal) is str else p_stopping_power_keV_um__internal
			)
	for i,v in enumerate(p_stopping_power_keV_um__internal):
		p_stopping_power_keV_um[i] = v
	
	return ret
	

def AT_Energy_MeV_u_from_Stopping_Power_single(p_stopping_power_source_no, p_Stopping_Power_MeV_cm2_g, p_particle_no, p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in] stopping_power_source_no
	@param[in] Stopping_Power_MeV_cm2_g
	@param[in] particle_no
	@param[in] material_no
	@return range [m]
	"""
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_Stopping_Power_MeV_cm2_g__internal = p_Stopping_Power_MeV_cm2_g
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_Energy_MeV_u_from_Stopping_Power_single(p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_Stopping_Power_MeV_cm2_g__internal.encode() if type(p_Stopping_Power_MeV_cm2_g__internal) is str else p_Stopping_Power_MeV_cm2_g__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_run_IGK_method(p_E_MeV_u, p_particle_no, p_fluence_cm2_or_dose_Gy, p_material_no, p_stopping_power_source_no, p_rdd_model, p_rdd_parameters, p_er_model, p_gamma_model, p_gamma_parameters, p_saturation_cross_section_factor, p_write_output, p_relative_efficiency, p_S_HCP, p_S_gamma, p_sI_cm2, p_gamma_dose_Gy, p_P_I, p_P_g):
	"""
	Wrapping function generated for C language function documented as follows:
	@brief Ion-gamma-kill model
	Computes HCP response and relative efficiency/RBE using Katz' Ion-Gamma-Kill approach
	according to Waligorski, 1988
	@param[in]      number_of_field_components       number of components in the mixed particle field
	@param[in]      E_MeV_u                          particle energy for each component in the mixed particle field [MeV/u] (array of size number_of_field_components)
	@param[in]      particle_no                      particle type for each component in the mixed particle field (array of size number_of_field_components)
	@see AT_DataParticle.h for definition
	@param[in]      fluence_cm2_or_dose_Gy           if positive, particle fluence for each component in the mixed particle field [1/cm2]; if negative, particle dose for each component in the mixed particle field [Gy] (array of size number_of_field_components)
	@param[in]      material_no                      index number for detector material
	@param[in]      stopping_power_source_no         stopping power source number (PSTAR,...)
	@see AT_DataMaterial.h for definition
	@param[in]      rdd_model                        index number for chosen radial dose distribution
	@param[in]      rdd_parameters                   parameters for chosen radial dose distribution (array of size 4)
	@see AT_RDD.h for definition
	@param[in]      er_model                         index number for chosen electron-range model
	@see AT_ElectronRange.h for definition
	@param[in]      gamma_model                      index number for chosen gamma response
	@param[in]      gamma_parameters                 parameters for chosen gamma response (array of size 9)
	@see AT_GammaResponse.h for definition
	@param[in]      saturation_cross_section_factor  scaling factor for the saturation cross section
	@see Waligorski, 1988
	@param[in]      write_output                     if true, a protocol is written to a file in the working directory
	@param[out]     relative_efficiency              particle response at dose D / gamma response at dose D
	@param[out]     S_HCP                            absolute particle response
	@param[out]     S_gamma                          absolute gamma response
	@param[out]     sI_cm2                           resulting ion saturation cross section in cm2
	@param[out]     gamma_dose_Gy                    dose contribution from gamma kills
	@param[out]     P_I                              ion kill probability
	@param[out]     P_g                              gamma kill probability
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2_or_dose_Gy,p_rdd_parameters,p_gamma_parameters]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2_or_dose_Gy]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_relative_efficiency)
	for in_array_argument in [p_relative_efficiency,p_S_HCP,p_S_gamma,p_sI_cm2,p_gamma_dose_Gy,p_P_I,p_P_g]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_relative_efficiency, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_S_HCP, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_S_gamma, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_sI_cm2, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_gamma_dose_Gy, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_P_I, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_P_g, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_relative_efficiency) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_relative_efficiency.clear()
		p_relative_efficiency += [0]
	
	if len(p_S_HCP) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_S_HCP.clear()
		p_S_HCP += [0]
	
	if len(p_S_gamma) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_S_gamma.clear()
		p_S_gamma += [0]
	
	if len(p_sI_cm2) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_sI_cm2.clear()
		p_sI_cm2 += [0]
	
	if len(p_gamma_dose_Gy) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_gamma_dose_Gy.clear()
		p_gamma_dose_Gy += [0]
	
	if len(p_P_I) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_P_I.clear()
		p_P_I += [0]
	
	if len(p_P_g) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_P_g.clear()
		p_P_g += [0]
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2_or_dose_Gy__internal = p_fluence_cm2_or_dose_Gy
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_rdd_model__internal = p_rdd_model
	p_rdd_parameters__internal = p_rdd_parameters
	p_er_model__internal = p_er_model
	p_gamma_model__internal = p_gamma_model
	p_gamma_parameters__internal = p_gamma_parameters
	p_saturation_cross_section_factor__internal = p_saturation_cross_section_factor
	p_write_output__internal = p_write_output
	p_relative_efficiency__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_relative_efficiency):
		p_relative_efficiency__internal[i] = v
	
	p_S_HCP__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_S_HCP):
		p_S_HCP__internal[i] = v
	
	p_S_gamma__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_S_gamma):
		p_S_gamma__internal[i] = v
	
	p_sI_cm2__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_sI_cm2):
		p_sI_cm2__internal[i] = v
	
	p_gamma_dose_Gy__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_gamma_dose_Gy):
		p_gamma_dose_Gy__internal[i] = v
	
	p_P_I__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_P_I):
		p_P_I__internal[i] = v
	
	p_P_g__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_P_g):
		p_P_g__internal[i] = v
	
	_libAT.lib.AT_run_IGK_method(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2_or_dose_Gy__internal.encode() if type(p_fluence_cm2_or_dose_Gy__internal) is str else p_fluence_cm2_or_dose_Gy__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_rdd_model__internal.encode() if type(p_rdd_model__internal) is str else p_rdd_model__internal
			,p_rdd_parameters__internal.encode() if type(p_rdd_parameters__internal) is str else p_rdd_parameters__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_gamma_model__internal.encode() if type(p_gamma_model__internal) is str else p_gamma_model__internal
			,p_gamma_parameters__internal.encode() if type(p_gamma_parameters__internal) is str else p_gamma_parameters__internal
			,p_saturation_cross_section_factor__internal.encode() if type(p_saturation_cross_section_factor__internal) is str else p_saturation_cross_section_factor__internal
			,p_write_output__internal.encode() if type(p_write_output__internal) is str else p_write_output__internal
			,p_relative_efficiency__internal.encode() if type(p_relative_efficiency__internal) is str else p_relative_efficiency__internal
			,p_S_HCP__internal.encode() if type(p_S_HCP__internal) is str else p_S_HCP__internal
			,p_S_gamma__internal.encode() if type(p_S_gamma__internal) is str else p_S_gamma__internal
			,p_sI_cm2__internal.encode() if type(p_sI_cm2__internal) is str else p_sI_cm2__internal
			,p_gamma_dose_Gy__internal.encode() if type(p_gamma_dose_Gy__internal) is str else p_gamma_dose_Gy__internal
			,p_P_I__internal.encode() if type(p_P_I__internal) is str else p_P_I__internal
			,p_P_g__internal.encode() if type(p_P_g__internal) is str else p_P_g__internal
			)
	for i,v in enumerate(p_relative_efficiency__internal):
		p_relative_efficiency[i] = v
	
	for i,v in enumerate(p_S_HCP__internal):
		p_S_HCP[i] = v
	
	for i,v in enumerate(p_S_gamma__internal):
		p_S_gamma[i] = v
	
	for i,v in enumerate(p_sI_cm2__internal):
		p_sI_cm2[i] = v
	
	for i,v in enumerate(p_gamma_dose_Gy__internal):
		p_gamma_dose_Gy[i] = v
	
	for i,v in enumerate(p_P_I__internal):
		p_P_I[i] = v
	
	for i,v in enumerate(p_P_g__internal):
		p_P_g[i] = v
	
	

def AT_Bethe_energy_loss_MeV_cm2_g(p_E_MeV_u, p_particle_no, p_material_no, p_E_restricted_keV, p_use_effective_charge, p_Mass_Stopping_Power_MeV_cm2_g):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the mass stopping power using the Bethe formula
	for many particles according to ICRU49, p.6, Eq. 2.1
	BUT WITHOUT shell, Bloch or Barkas correction!
	@param[in]  	   n      		number of particles
	@param[in]  	   E_MeV_u      energies of particle per nucleon (array of size n)
	@param[in]  	   particle_no  particle indices (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  material index (single value)
	@see          AT_DataMaterial.h for definition
	@param[in]      E_restricted_keV 	if positive and smaller than maximally transferable energy, the restricted stopping power will be computed (single value)
	@param[in]      use_effective_charge 	TODO
	@param[out]     Mass_Stopping_Power_MeV_cm2_g (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_Mass_Stopping_Power_MeV_cm2_g is passed correctly:
	if len(p_Mass_Stopping_Power_MeV_cm2_g) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_Mass_Stopping_Power_MeV_cm2_g was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_Mass_Stopping_Power_MeV_cm2_g.clear()
		p_Mass_Stopping_Power_MeV_cm2_g += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_E_restricted_keV__internal = p_E_restricted_keV
	p_use_effective_charge__internal = p_use_effective_charge
	p_Mass_Stopping_Power_MeV_cm2_g__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_Mass_Stopping_Power_MeV_cm2_g):
		p_Mass_Stopping_Power_MeV_cm2_g__internal[i] = v
	
	_libAT.lib.AT_Bethe_energy_loss_MeV_cm2_g(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_E_restricted_keV__internal.encode() if type(p_E_restricted_keV__internal) is str else p_E_restricted_keV__internal
			,p_use_effective_charge__internal.encode() if type(p_use_effective_charge__internal) is str else p_use_effective_charge__internal
			,p_Mass_Stopping_Power_MeV_cm2_g__internal.encode() if type(p_Mass_Stopping_Power_MeV_cm2_g__internal) is str else p_Mass_Stopping_Power_MeV_cm2_g__internal
			)
	for i,v in enumerate(p_Mass_Stopping_Power_MeV_cm2_g__internal):
		p_Mass_Stopping_Power_MeV_cm2_g[i] = v
	
	

def AT_RDD_name_from_number(p_RDD_no, p_RDD_name):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns name of the radial dose distribution model from model number
	@param[in]   RDD_no   radial dose distribution model number
	@param[out]  RDD_name string containing radial dose distribution model name
	@return      status code
	"""
	if not isinstance(p_RDD_name, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_RDD_name) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_RDD_name.clear()
		p_RDD_name += ['']
	
	p_RDD_no__internal = p_RDD_no
	arg_keepalive = [ffi.new("char[]", 1)]
	p_RDD_name__internal = ffi.new("char* []", arg_keepalive)
	ret = _libAT.lib.AT_RDD_name_from_number(p_RDD_no__internal.encode() if type(p_RDD_no__internal) is str else p_RDD_no__internal
			,p_RDD_name__internal[0].encode() if type(p_RDD_name__internal[0]) is str else p_RDD_name__internal[0]
			)
	for i,v in enumerate(p_RDD_name__internal):
		p_RDD_name[i] = ffi.string(v).decode()
	
	return ret
	

def AT_RDD_number_from_name(p_RDD_name):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns number of the radial dose distribution model from its name
	@param[in]   RDD_name  string containing radial dose distribution model name
	@return      RDD_no    radial dose distribution model index
	"""
	p_RDD_name__internal = p_RDD_name
	ret = _libAT.lib.AT_RDD_number_from_name(p_RDD_name__internal.encode() if type(p_RDD_name__internal) is str else p_RDD_name__internal
			)
	return ret
	

def AT_RDD_number_of_parameters(p_RDD_model):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns number of parameters of the radial dose distribution model from model number
	@param[in]   RDD_model   radial dose distribution model number
	return                   number of RDD parameters
	"""
	p_RDD_model__internal = p_RDD_model
	ret = _libAT.lib.AT_RDD_number_of_parameters(p_RDD_model__internal.encode() if type(p_RDD_model__internal) is str else p_RDD_model__internal
			)
	return ret
	

def AT_D_RDD_Gy(p_r_m, p_E_MeV_u, p_particle_no, p_material_no, p_rdd_model, p_rdd_parameter, p_er_model, p_stopping_power_source_no, p_D_RDD_Gy):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns local dose as a function of distance r_m for a given radial dose distribution model
	@param[in]   n              number of particles (length of r_m vector)
	@param[in]   r_m            distance [m] (array of size n)
	@param[in]   E_MeV_u        particle (ion) energy per nucleon [MeV/u] (single number, no mixed fields)
	@param[in]   particle_no    particle code number (single number, no mixed fields)
	@param[in]   material_no    material code number (single number, no mixed fields)
	@param[in]   rdd_model      radial dose distribution model index
	@param[in]   rdd_parameter  radial dose distribution model parameters (array of size 4)
	@param[in]   er_model       electron range / track with model index
	@param[in]   stopping_power_source_no  TODO
	@param[out]  D_RDD_Gy       dose [Gy] (array of size n)
	@return status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_r_m,p_rdd_parameter]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_D_RDD_Gy is passed correctly:
	if len(p_D_RDD_Gy) != len(p_r_m):
		out_array_auto_init = "\nWarning: OUT array parameter p_D_RDD_Gy was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_D_RDD_Gy.clear()
		p_D_RDD_Gy += [0]*len(p_r_m)
	
	# Array sizes variables initialization:
	p_n = len(p_r_m)
	p_n__internal = p_n
	p_r_m__internal = p_r_m
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_rdd_model__internal = p_rdd_model
	p_rdd_parameter__internal = p_rdd_parameter
	p_er_model__internal = p_er_model
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_D_RDD_Gy__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_D_RDD_Gy):
		p_D_RDD_Gy__internal[i] = v
	
	ret = _libAT.lib.AT_D_RDD_Gy(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_r_m__internal.encode() if type(p_r_m__internal) is str else p_r_m__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_rdd_model__internal.encode() if type(p_rdd_model__internal) is str else p_rdd_model__internal
			,p_rdd_parameter__internal.encode() if type(p_rdd_parameter__internal) is str else p_rdd_parameter__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_D_RDD_Gy__internal.encode() if type(p_D_RDD_Gy__internal) is str else p_D_RDD_Gy__internal
			)
	for i,v in enumerate(p_D_RDD_Gy__internal):
		p_D_RDD_Gy[i] = v
	
	return ret
	

def AT_r_RDD_m(p_D_RDD_Gy, p_E_MeV_u, p_particle_no, p_material_no, p_rdd_model, p_rdd_parameter, p_er_model, p_stopping_power_source_no, p_r_RDD_m):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns distance as a function of dose
	@param[in]   n                   number of particles (length of D_RDD_Gy vector)
	@param[in]   D_RDD_Gy            dose [Gy] (array of size n)
	@param[in]   E_MeV_u             particle (ion) energy per nucleon [MeV/u]
	@param[in]   particle_no         particle code number
	@param[in]   material_no         material code number
	@param[in]   rdd_model           Radial Dose Distribution model code number
	@param[in]   rdd_parameter       Radial Dose Distribution model parameters vector (array of size 4)
	@param[in]   er_model            delta electron range model code number
	@param[in]   stopping_power_source_no   TODO
	@param[out]  r_RDD_m             distance [m] (array of size n)
	@return status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_D_RDD_Gy,p_rdd_parameter]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_r_RDD_m is passed correctly:
	if len(p_r_RDD_m) != len(p_D_RDD_Gy):
		out_array_auto_init = "\nWarning: OUT array parameter p_r_RDD_m was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_r_RDD_m.clear()
		p_r_RDD_m += [0]*len(p_D_RDD_Gy)
	
	# Array sizes variables initialization:
	p_n = len(p_D_RDD_Gy)
	p_n__internal = p_n
	p_D_RDD_Gy__internal = p_D_RDD_Gy
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_rdd_model__internal = p_rdd_model
	p_rdd_parameter__internal = p_rdd_parameter
	p_er_model__internal = p_er_model
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_r_RDD_m__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_r_RDD_m):
		p_r_RDD_m__internal[i] = v
	
	ret = _libAT.lib.AT_r_RDD_m(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_D_RDD_Gy__internal.encode() if type(p_D_RDD_Gy__internal) is str else p_D_RDD_Gy__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_rdd_model__internal.encode() if type(p_rdd_model__internal) is str else p_rdd_model__internal
			,p_rdd_parameter__internal.encode() if type(p_rdd_parameter__internal) is str else p_rdd_parameter__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_r_RDD_m__internal.encode() if type(p_r_RDD_m__internal) is str else p_r_RDD_m__internal
			)
	for i,v in enumerate(p_r_RDD_m__internal):
		p_r_RDD_m[i] = v
	
	return ret
	

def AT_RDD_ExtendedTarget_KatzPoint_Gy(p_r_m, p_a0_m, p_er_model, p_KatzPoint_r_min_m, p_max_electron_range_m, p_alpha, p_Katz_plateau_Gy, p_Katz_point_coeff_Gy):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in] r_m
	@param[in] a0_m
	@param[in] er_model
	@param[in] KatzPoint_r_min_m
	@param[in] max_electron_range_m
	@param[in] alpha
	@param[in] Katz_plateau_Gy
	@param[in] Katz_point_coeff_Gy
	@return
	"""
	p_r_m__internal = p_r_m
	p_a0_m__internal = p_a0_m
	p_er_model__internal = p_er_model
	p_KatzPoint_r_min_m__internal = p_KatzPoint_r_min_m
	p_max_electron_range_m__internal = p_max_electron_range_m
	p_alpha__internal = p_alpha
	p_Katz_plateau_Gy__internal = p_Katz_plateau_Gy
	p_Katz_point_coeff_Gy__internal = p_Katz_point_coeff_Gy
	ret = _libAT.lib.AT_RDD_ExtendedTarget_KatzPoint_Gy(p_r_m__internal.encode() if type(p_r_m__internal) is str else p_r_m__internal
			,p_a0_m__internal.encode() if type(p_a0_m__internal) is str else p_a0_m__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_KatzPoint_r_min_m__internal.encode() if type(p_KatzPoint_r_min_m__internal) is str else p_KatzPoint_r_min_m__internal
			,p_max_electron_range_m__internal.encode() if type(p_max_electron_range_m__internal) is str else p_max_electron_range_m__internal
			,p_alpha__internal.encode() if type(p_alpha__internal) is str else p_alpha__internal
			,p_Katz_plateau_Gy__internal.encode() if type(p_Katz_plateau_Gy__internal) is str else p_Katz_plateau_Gy__internal
			,p_Katz_point_coeff_Gy__internal.encode() if type(p_Katz_point_coeff_Gy__internal) is str else p_Katz_point_coeff_Gy__internal
			)
	return ret
	

def AT_inverse_RDD_ExtendedTarget_KatzPoint_m(p_D_Gy, p_r_min_m, p_max_electron_range_m, p_a0_m, p_er_model, p_alpha, p_Katz_plateau_Gy, p_Katz_point_coeff_Gy):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in] D_Gy
	@param[in] r_min_m
	@param[in] max_electron_range_m
	@param[in] a0_m
	@param[in] er_model
	@param[in] alpha
	@param[in] Katz_plateau_Gy
	@param[in] Katz_point_coeff_Gy
	@return
	"""
	p_D_Gy__internal = p_D_Gy
	p_r_min_m__internal = p_r_min_m
	p_max_electron_range_m__internal = p_max_electron_range_m
	p_a0_m__internal = p_a0_m
	p_er_model__internal = p_er_model
	p_alpha__internal = p_alpha
	p_Katz_plateau_Gy__internal = p_Katz_plateau_Gy
	p_Katz_point_coeff_Gy__internal = p_Katz_point_coeff_Gy
	ret = _libAT.lib.AT_inverse_RDD_ExtendedTarget_KatzPoint_m(p_D_Gy__internal.encode() if type(p_D_Gy__internal) is str else p_D_Gy__internal
			,p_r_min_m__internal.encode() if type(p_r_min_m__internal) is str else p_r_min_m__internal
			,p_max_electron_range_m__internal.encode() if type(p_max_electron_range_m__internal) is str else p_max_electron_range_m__internal
			,p_a0_m__internal.encode() if type(p_a0_m__internal) is str else p_a0_m__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_alpha__internal.encode() if type(p_alpha__internal) is str else p_alpha__internal
			,p_Katz_plateau_Gy__internal.encode() if type(p_Katz_plateau_Gy__internal) is str else p_Katz_plateau_Gy__internal
			,p_Katz_point_coeff_Gy__internal.encode() if type(p_Katz_point_coeff_Gy__internal) is str else p_Katz_point_coeff_Gy__internal
			)
	return ret
	

def AT_RDD_ExtendedTarget_CucinottaPoint_Gy_by_integration(p_r_m, p_a0_m, p_KatzPoint_r_min_m, p_max_electron_range_m, p_beta, p_Katz_point_coeff_Gy, p_C_norm):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in] r_m
	@param[in] a0_m
	@param[in] KatzPoint_r_min_m
	@param[in] max_electron_range_m
	@param[in] beta
	@param[in] Katz_point_coeff_Gy
	@param[in] C_norm
	@return
	"""
	p_r_m__internal = p_r_m
	p_a0_m__internal = p_a0_m
	p_KatzPoint_r_min_m__internal = p_KatzPoint_r_min_m
	p_max_electron_range_m__internal = p_max_electron_range_m
	p_beta__internal = p_beta
	p_Katz_point_coeff_Gy__internal = p_Katz_point_coeff_Gy
	p_C_norm__internal = p_C_norm
	ret = _libAT.lib.AT_RDD_ExtendedTarget_CucinottaPoint_Gy_by_integration(p_r_m__internal.encode() if type(p_r_m__internal) is str else p_r_m__internal
			,p_a0_m__internal.encode() if type(p_a0_m__internal) is str else p_a0_m__internal
			,p_KatzPoint_r_min_m__internal.encode() if type(p_KatzPoint_r_min_m__internal) is str else p_KatzPoint_r_min_m__internal
			,p_max_electron_range_m__internal.encode() if type(p_max_electron_range_m__internal) is str else p_max_electron_range_m__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			,p_Katz_point_coeff_Gy__internal.encode() if type(p_Katz_point_coeff_Gy__internal) is str else p_Katz_point_coeff_Gy__internal
			,p_C_norm__internal.encode() if type(p_C_norm__internal) is str else p_C_norm__internal
			)
	return ret
	

def AT_RDD_ExtendedTarget_CucinottaPoint_Gy(p_r_m, p_a0_m, p_KatzPoint_r_min_m, p_max_electron_range_m, p_beta, p_Katz_point_coeff_Gy, p_C_norm, p_Cucinotta_plateau_Gy):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in] r_m
	@param[in] a0_m
	@param[in] KatzPoint_r_min_m
	@param[in] max_electron_range_m
	@param[in] beta
	@param[in] Katz_point_coeff_Gy
	@param[in] C_norm
	@param[in] Cucinotta_plateau_Gy
	@return
	"""
	p_r_m__internal = p_r_m
	p_a0_m__internal = p_a0_m
	p_KatzPoint_r_min_m__internal = p_KatzPoint_r_min_m
	p_max_electron_range_m__internal = p_max_electron_range_m
	p_beta__internal = p_beta
	p_Katz_point_coeff_Gy__internal = p_Katz_point_coeff_Gy
	p_C_norm__internal = p_C_norm
	p_Cucinotta_plateau_Gy__internal = p_Cucinotta_plateau_Gy
	ret = _libAT.lib.AT_RDD_ExtendedTarget_CucinottaPoint_Gy(p_r_m__internal.encode() if type(p_r_m__internal) is str else p_r_m__internal
			,p_a0_m__internal.encode() if type(p_a0_m__internal) is str else p_a0_m__internal
			,p_KatzPoint_r_min_m__internal.encode() if type(p_KatzPoint_r_min_m__internal) is str else p_KatzPoint_r_min_m__internal
			,p_max_electron_range_m__internal.encode() if type(p_max_electron_range_m__internal) is str else p_max_electron_range_m__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			,p_Katz_point_coeff_Gy__internal.encode() if type(p_Katz_point_coeff_Gy__internal) is str else p_Katz_point_coeff_Gy__internal
			,p_C_norm__internal.encode() if type(p_C_norm__internal) is str else p_C_norm__internal
			,p_Cucinotta_plateau_Gy__internal.encode() if type(p_Cucinotta_plateau_Gy__internal) is str else p_Cucinotta_plateau_Gy__internal
			)
	return ret
	

def AT_inverse_RDD_ExtendedTarget_CucinottaPoint_m(p_D_Gy, p_a0_m, p_KatzPoint_r_min_m, p_max_electron_range_m, p_beta, p_Katz_point_coeff_Gy, p_C_norm, p_Cucinotta_plateau_Gy):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in] D_Gy
	@param[in] a0_m
	@param[in] KatzPoint_r_min_m
	@param[in] max_electron_range_m
	@param[in] beta
	@param[in] Katz_point_coeff_Gy
	@param[in] C_norm
	@param[in] Cucinotta_plateau_Gy
	@return
	"""
	p_D_Gy__internal = p_D_Gy
	p_a0_m__internal = p_a0_m
	p_KatzPoint_r_min_m__internal = p_KatzPoint_r_min_m
	p_max_electron_range_m__internal = p_max_electron_range_m
	p_beta__internal = p_beta
	p_Katz_point_coeff_Gy__internal = p_Katz_point_coeff_Gy
	p_C_norm__internal = p_C_norm
	p_Cucinotta_plateau_Gy__internal = p_Cucinotta_plateau_Gy
	ret = _libAT.lib.AT_inverse_RDD_ExtendedTarget_CucinottaPoint_m(p_D_Gy__internal.encode() if type(p_D_Gy__internal) is str else p_D_Gy__internal
			,p_a0_m__internal.encode() if type(p_a0_m__internal) is str else p_a0_m__internal
			,p_KatzPoint_r_min_m__internal.encode() if type(p_KatzPoint_r_min_m__internal) is str else p_KatzPoint_r_min_m__internal
			,p_max_electron_range_m__internal.encode() if type(p_max_electron_range_m__internal) is str else p_max_electron_range_m__internal
			,p_beta__internal.encode() if type(p_beta__internal) is str else p_beta__internal
			,p_Katz_point_coeff_Gy__internal.encode() if type(p_Katz_point_coeff_Gy__internal) is str else p_Katz_point_coeff_Gy__internal
			,p_C_norm__internal.encode() if type(p_C_norm__internal) is str else p_C_norm__internal
			,p_Cucinotta_plateau_Gy__internal.encode() if type(p_Cucinotta_plateau_Gy__internal) is str else p_Cucinotta_plateau_Gy__internal
			)
	return ret
	

def AT_run_GSM_method(p_E_MeV_u, p_particle_no, p_fluence_cm2_or_dose_Gy, p_material_no, p_stopping_power_source_no, p_rdd_model, p_rdd_parameters, p_er_model, p_gamma_model, p_gamma_parameters, p_N_runs, p_write_output, p_nX, p_voxel_size_m, p_lethal_events_mode, p_relative_efficiency, p_d_check, p_S_HCP, p_S_gamma, p_n_particles, p_sd_relative_efficiency, p_sd_d_check, p_sd_S_HCP, p_sd_S_gamma, p_sd_n_particles):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes HCP response and relative efficiency/RBE using summation of tracks
	an a Cartesian grid (the 'GSM' algorithm).
	Be aware that this routine can take considerable time to compute depending on
	the arguments, esp. for higher energy (>10 MeV/u) particles. It is therefore
	advantageous to test your settings with a low number of runs first.
	@param[in]      number_of_field_components     number of components in the mixed particle field
	@param[in]      E_MeV_u                        particle energy for each component in the mixed particle field [MeV/u] (array of size number_of_field_components)
	@param[in]      particle_no                    particle type for each component in the mixed particle field (array of size number_of_field_components)
	@see AT_DataParticle.h for definition
	@param[in]      fluence_cm2_or_dose_Gy         if positive, particle fluence for each component in the mixed particle field [1/cm2]; if negative, particle dose for each component in the mixed particle field [Gy] (array of size number_of_field_components)
	@param[in]      material_no                    index number for detector material
	@param[in]      stopping_power_source_no       TODO
	@see AT_DataMaterial.h for definition
	@param[in]      rdd_model                      index number for chosen radial dose distribution
	@param[in]      rdd_parameters                 parameters for chosen radial dose distribution (array of size 4)
	@see AT_RDD.h for definition
	@param[in]      er_model                       index number for chosen electron-range model
	@see AT_ElectronRange.h for definition
	@param[in]      gamma_model                    index number for chosen gamma response
	@param[in]      gamma_parameters               parameters for chosen gamma response (array of size 9)
	@see AT_GammaResponse.h for definition
	@param[in]      N_runs                         number of runs within which track positions will be resampled
	@param[in]      write_output                   if true, a protocol is written to "SuccessiveConvolutions.txt" in the working directory
	@param[in]      nX                             number of voxels of the grid in x (and y as the grid is quadratic)
	@param[in]      voxel_size_m                   side length of a voxel in m
	@param[in]      lethal_events_mode             if true, allows to do calculations for cell survival
	@param[out]     relative_efficiency            particle response at dose D / gamma response at dose D
	@param[out]     d_check                        sanity check:  total dose (in Gy) as returned by the algorithm
	@param[out]     S_HCP                          absolute particle response
	@param[out]     S_gamma                        absolute gamma response
	@param[out]     n_particles                    average number of particle tracks on the detector grid
	@param[out]     sd_relative_efficiency         standard deviation for relative_efficiency
	@param[out]     sd_d_check                     standard deviation for d_check
	@param[out]     sd_S_HCP                       standard deviation for S_HCP
	@param[out]     sd_S_gamma                     standard deviation for S_gamma
	@param[out]     sd_n_particles                 standard deviation for n_particles
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2_or_dose_Gy,p_rdd_parameters,p_gamma_parameters]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no,p_fluence_cm2_or_dose_Gy]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_relative_efficiency)
	for in_array_argument in [p_relative_efficiency,p_d_check,p_S_HCP,p_S_gamma,p_n_particles,p_sd_relative_efficiency,p_sd_d_check,p_sd_S_HCP,p_sd_S_gamma,p_sd_n_particles]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_relative_efficiency, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_d_check, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_S_HCP, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_S_gamma, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_n_particles, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_sd_relative_efficiency, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_sd_d_check, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_sd_S_HCP, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_sd_S_gamma, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_sd_n_particles, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_relative_efficiency) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_relative_efficiency.clear()
		p_relative_efficiency += [0]
	
	if len(p_d_check) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_d_check.clear()
		p_d_check += [0]
	
	if len(p_S_HCP) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_S_HCP.clear()
		p_S_HCP += [0]
	
	if len(p_S_gamma) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_S_gamma.clear()
		p_S_gamma += [0]
	
	if len(p_n_particles) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_n_particles.clear()
		p_n_particles += [0]
	
	if len(p_sd_relative_efficiency) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_sd_relative_efficiency.clear()
		p_sd_relative_efficiency += [0]
	
	if len(p_sd_d_check) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_sd_d_check.clear()
		p_sd_d_check += [0]
	
	if len(p_sd_S_HCP) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_sd_S_HCP.clear()
		p_sd_S_HCP += [0]
	
	if len(p_sd_S_gamma) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_sd_S_gamma.clear()
		p_sd_S_gamma += [0]
	
	if len(p_sd_n_particles) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_sd_n_particles.clear()
		p_sd_n_particles += [0]
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_fluence_cm2_or_dose_Gy__internal = p_fluence_cm2_or_dose_Gy
	p_material_no__internal = p_material_no
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_rdd_model__internal = p_rdd_model
	p_rdd_parameters__internal = p_rdd_parameters
	p_er_model__internal = p_er_model
	p_gamma_model__internal = p_gamma_model
	p_gamma_parameters__internal = p_gamma_parameters
	p_N_runs__internal = p_N_runs
	p_write_output__internal = p_write_output
	p_nX__internal = p_nX
	p_voxel_size_m__internal = p_voxel_size_m
	p_lethal_events_mode__internal = p_lethal_events_mode
	p_relative_efficiency__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_relative_efficiency):
		p_relative_efficiency__internal[i] = v
	
	p_d_check__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_d_check):
		p_d_check__internal[i] = v
	
	p_S_HCP__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_S_HCP):
		p_S_HCP__internal[i] = v
	
	p_S_gamma__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_S_gamma):
		p_S_gamma__internal[i] = v
	
	p_n_particles__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_n_particles):
		p_n_particles__internal[i] = v
	
	p_sd_relative_efficiency__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_sd_relative_efficiency):
		p_sd_relative_efficiency__internal[i] = v
	
	p_sd_d_check__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_sd_d_check):
		p_sd_d_check__internal[i] = v
	
	p_sd_S_HCP__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_sd_S_HCP):
		p_sd_S_HCP__internal[i] = v
	
	p_sd_S_gamma__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_sd_S_gamma):
		p_sd_S_gamma__internal[i] = v
	
	p_sd_n_particles__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_sd_n_particles):
		p_sd_n_particles__internal[i] = v
	
	_libAT.lib.AT_run_GSM_method(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2_or_dose_Gy__internal.encode() if type(p_fluence_cm2_or_dose_Gy__internal) is str else p_fluence_cm2_or_dose_Gy__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_rdd_model__internal.encode() if type(p_rdd_model__internal) is str else p_rdd_model__internal
			,p_rdd_parameters__internal.encode() if type(p_rdd_parameters__internal) is str else p_rdd_parameters__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_gamma_model__internal.encode() if type(p_gamma_model__internal) is str else p_gamma_model__internal
			,p_gamma_parameters__internal.encode() if type(p_gamma_parameters__internal) is str else p_gamma_parameters__internal
			,p_N_runs__internal.encode() if type(p_N_runs__internal) is str else p_N_runs__internal
			,p_write_output__internal.encode() if type(p_write_output__internal) is str else p_write_output__internal
			,p_nX__internal.encode() if type(p_nX__internal) is str else p_nX__internal
			,p_voxel_size_m__internal.encode() if type(p_voxel_size_m__internal) is str else p_voxel_size_m__internal
			,p_lethal_events_mode__internal.encode() if type(p_lethal_events_mode__internal) is str else p_lethal_events_mode__internal
			,p_relative_efficiency__internal.encode() if type(p_relative_efficiency__internal) is str else p_relative_efficiency__internal
			,p_d_check__internal.encode() if type(p_d_check__internal) is str else p_d_check__internal
			,p_S_HCP__internal.encode() if type(p_S_HCP__internal) is str else p_S_HCP__internal
			,p_S_gamma__internal.encode() if type(p_S_gamma__internal) is str else p_S_gamma__internal
			,p_n_particles__internal.encode() if type(p_n_particles__internal) is str else p_n_particles__internal
			,p_sd_relative_efficiency__internal.encode() if type(p_sd_relative_efficiency__internal) is str else p_sd_relative_efficiency__internal
			,p_sd_d_check__internal.encode() if type(p_sd_d_check__internal) is str else p_sd_d_check__internal
			,p_sd_S_HCP__internal.encode() if type(p_sd_S_HCP__internal) is str else p_sd_S_HCP__internal
			,p_sd_S_gamma__internal.encode() if type(p_sd_S_gamma__internal) is str else p_sd_S_gamma__internal
			,p_sd_n_particles__internal.encode() if type(p_sd_n_particles__internal) is str else p_sd_n_particles__internal
			)
	for i,v in enumerate(p_relative_efficiency__internal):
		p_relative_efficiency[i] = v
	
	for i,v in enumerate(p_d_check__internal):
		p_d_check[i] = v
	
	for i,v in enumerate(p_S_HCP__internal):
		p_S_HCP[i] = v
	
	for i,v in enumerate(p_S_gamma__internal):
		p_S_gamma[i] = v
	
	for i,v in enumerate(p_n_particles__internal):
		p_n_particles[i] = v
	
	for i,v in enumerate(p_sd_relative_efficiency__internal):
		p_sd_relative_efficiency[i] = v
	
	for i,v in enumerate(p_sd_d_check__internal):
		p_sd_d_check[i] = v
	
	for i,v in enumerate(p_sd_S_HCP__internal):
		p_sd_S_HCP[i] = v
	
	for i,v in enumerate(p_sd_S_gamma__internal):
		p_sd_S_gamma[i] = v
	
	for i,v in enumerate(p_sd_n_particles__internal):
		p_sd_n_particles[i] = v
	
	

def AT_GSM_local_dose_distrib(p_E_MeV_u, p_fluence_cm2, p_particle_no, p_material_no, p_rdd_model, p_rdd_parameter, p_er_model, p_stopping_power_source_no, p_nX, p_pixel_size_m, p_number_of_bins, p_dose_bin_centers_Gy, p_random_number_generator_seed, p_zero_dose_fraction, p_dose_frequency_Gy):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes local dose histogram for given mixed field
	@param[in]  number_of_field_components                number of particle types in the mixed particle field
	@param[in]  E_MeV_u                                   energy of particles in the mixed particle field (array of size number_of_field_components)
	@param[in]  fluence_cm2                               fluences for the given particles (array of size number_of_field_components)
	@param[in]  particle_no                               type of the particles in the mixed particle field (array of size number_of_field_components)
	@see          AT_DataParticle.h for definition
	@param[in]  material_no                               index number for detector material
	@see          AT_DataMaterial.h for definition
	@param[in]  rdd_model                                 index number for chosen radial dose distribution
	@param[in]  rdd_parameter                             parameters for chosen radial dose distribution (array of size depending on chosen model)
	@see          AT_RDD.h for definition
	@param[in]  er_model                                  index number for chosen electron-range model
	@see          AT_ElectronRange.h for definition
	@param[in] stopping_power_source_no                   TODO
	@param[in] nX                                         TODO
	@param[in] pixel_size_m                               TODO
	@param[in] number_of_bins                             TODO
	@param[in] dose_bin_centers_Gy                        TODO
	@param[out] random_number_generator_seed              TODO
	@param[out] zero_dose_fraction                        TODO
	@param[out] dose_frequency_Gy                         TODO
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_fluence_cm2,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_fluence_cm2,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_random_number_generator_seed)
	for in_array_argument in [p_random_number_generator_seed,p_zero_dose_fraction,p_dose_frequency_Gy]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_random_number_generator_seed, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_zero_dose_fraction, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_dose_frequency_Gy, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_random_number_generator_seed) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_random_number_generator_seed.clear()
		p_random_number_generator_seed += [0]
	
	if len(p_zero_dose_fraction) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_zero_dose_fraction.clear()
		p_zero_dose_fraction += [0]
	
	if len(p_dose_frequency_Gy) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_dose_frequency_Gy.clear()
		p_dose_frequency_Gy += [0]
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_fluence_cm2__internal = p_fluence_cm2
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_rdd_model__internal = p_rdd_model
	p_rdd_parameter__internal = p_rdd_parameter
	p_er_model__internal = p_er_model
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_nX__internal = p_nX
	p_pixel_size_m__internal = p_pixel_size_m
	p_number_of_bins__internal = p_number_of_bins
	p_dose_bin_centers_Gy__internal = p_dose_bin_centers_Gy
	p_random_number_generator_seed__internal = ffi.new("unsigned long[]", 1)
	for i,v in enumerate(p_random_number_generator_seed):
		p_random_number_generator_seed__internal[i] = v
	
	p_zero_dose_fraction__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_zero_dose_fraction):
		p_zero_dose_fraction__internal[i] = v
	
	p_dose_frequency_Gy__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_dose_frequency_Gy):
		p_dose_frequency_Gy__internal[i] = v
	
	_libAT.lib.AT_GSM_local_dose_distrib(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_rdd_model__internal.encode() if type(p_rdd_model__internal) is str else p_rdd_model__internal
			,p_rdd_parameter__internal.encode() if type(p_rdd_parameter__internal) is str else p_rdd_parameter__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_nX__internal.encode() if type(p_nX__internal) is str else p_nX__internal
			,p_pixel_size_m__internal.encode() if type(p_pixel_size_m__internal) is str else p_pixel_size_m__internal
			,p_number_of_bins__internal.encode() if type(p_number_of_bins__internal) is str else p_number_of_bins__internal
			,p_dose_bin_centers_Gy__internal.encode() if type(p_dose_bin_centers_Gy__internal) is str else p_dose_bin_centers_Gy__internal
			,p_random_number_generator_seed__internal.encode() if type(p_random_number_generator_seed__internal) is str else p_random_number_generator_seed__internal
			,p_zero_dose_fraction__internal.encode() if type(p_zero_dose_fraction__internal) is str else p_zero_dose_fraction__internal
			,p_dose_frequency_Gy__internal.encode() if type(p_dose_frequency_Gy__internal) is str else p_dose_frequency_Gy__internal
			)
	for i,v in enumerate(p_random_number_generator_seed__internal):
		p_random_number_generator_seed[i] = v
	
	for i,v in enumerate(p_zero_dose_fraction__internal):
		p_zero_dose_fraction[i] = v
	
	for i,v in enumerate(p_dose_frequency_Gy__internal):
		p_dose_frequency_Gy[i] = v
	
	

def AT_GSM_multiple_local_dose_distrib(p_E_MeV_u, p_fluence_cm2, p_particle_no, p_material_no, p_rdd_model, p_rdd_parameter, p_er_model, p_stopping_power_source_no, p_nX, p_pixel_size_m, p_N_runs, p_N_repetitions, p_dose_bin_centers_Gy, p_dose_bin_width_Gy, p_mean_d_check_Gy, p_sd_d_check_Gy, p_mean_zero_dose_fraction, p_sd_zero_dose_fraction, p_mean_dose_frequency_Gy, p_sd_dose_frequency_Gy):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in] number_of_field_components
	@param[in] E_MeV_u (array of size number_of_field_components)
	@param[in] fluence_cm2 (array of size number_of_field_components)
	@param[in] particle_no (array of size number_of_field_components)
	@param[in] material_no
	@param[in] rdd_model
	@param[in] rdd_parameter (array of size 4)
	@param[in] er_model
	@param[in] stopping_power_source_no
	@param[in] nX
	@param[in] pixel_size_m
	@param[in] N_runs
	@param[in] N_repetitions
	@param[in] number_of_bins
	@param[in] dose_bin_centers_Gy (array of size number_of_bins)
	@param[out] dose_bin_width_Gy (array of size number_of_bins)
	@param[out] mean_d_check_Gy
	@param[out] sd_d_check_Gy
	@param[out] mean_zero_dose_fraction
	@param[out] sd_zero_dose_fraction
	@param[out] mean_dose_frequency_Gy (array of size number_of_bins)
	@param[out] sd_dose_frequency_Gy (array of size number_of_bins)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_fluence_cm2,p_particle_no,p_rdd_parameter,p_dose_bin_centers_Gy]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: number_of_field_components
	declared_in_arr_param_size__number_of_field_components = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_fluence_cm2,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__number_of_field_components:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_dose_bin_width_Gy is passed correctly:
	if len(p_dose_bin_width_Gy) != len(p_dose_bin_centers_Gy):
		out_array_auto_init = "\nWarning: OUT array parameter p_dose_bin_width_Gy was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_dose_bin_width_Gy.clear()
		p_dose_bin_width_Gy += [0]*len(p_dose_bin_centers_Gy)
	
	# Procedure to check if OUT array p_mean_dose_frequency_Gy is passed correctly:
	if len(p_mean_dose_frequency_Gy) != len(p_dose_bin_centers_Gy):
		out_array_auto_init = "\nWarning: OUT array parameter p_mean_dose_frequency_Gy was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_mean_dose_frequency_Gy.clear()
		p_mean_dose_frequency_Gy += [0]*len(p_dose_bin_centers_Gy)
	
	# Procedure to check if OUT array p_sd_dose_frequency_Gy is passed correctly:
	if len(p_sd_dose_frequency_Gy) != len(p_dose_bin_centers_Gy):
		out_array_auto_init = "\nWarning: OUT array parameter p_sd_dose_frequency_Gy was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_sd_dose_frequency_Gy.clear()
		p_sd_dose_frequency_Gy += [0]*len(p_dose_bin_centers_Gy)
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_mean_d_check_Gy)
	for in_array_argument in [p_mean_d_check_Gy,p_sd_d_check_Gy,p_mean_zero_dose_fraction,p_sd_zero_dose_fraction]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_mean_d_check_Gy, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_sd_d_check_Gy, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_mean_zero_dose_fraction, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_sd_zero_dose_fraction, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_mean_d_check_Gy) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_mean_d_check_Gy.clear()
		p_mean_d_check_Gy += [0]
	
	if len(p_sd_d_check_Gy) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_sd_d_check_Gy.clear()
		p_sd_d_check_Gy += [0]
	
	if len(p_mean_zero_dose_fraction) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_mean_zero_dose_fraction.clear()
		p_mean_zero_dose_fraction += [0]
	
	if len(p_sd_zero_dose_fraction) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_sd_zero_dose_fraction.clear()
		p_sd_zero_dose_fraction += [0]
	
	# Array sizes variables initialization:
	p_number_of_field_components = len(p_E_MeV_u)
	p_number_of_bins = len(p_dose_bin_centers_Gy)
	p_number_of_field_components__internal = p_number_of_field_components
	p_E_MeV_u__internal = p_E_MeV_u
	p_fluence_cm2__internal = p_fluence_cm2
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_rdd_model__internal = p_rdd_model
	p_rdd_parameter__internal = p_rdd_parameter
	p_er_model__internal = p_er_model
	p_stopping_power_source_no__internal = p_stopping_power_source_no
	p_nX__internal = p_nX
	p_pixel_size_m__internal = p_pixel_size_m
	p_N_runs__internal = p_N_runs
	p_N_repetitions__internal = p_N_repetitions
	p_number_of_bins__internal = p_number_of_bins
	p_dose_bin_centers_Gy__internal = p_dose_bin_centers_Gy
	p_dose_bin_width_Gy__internal = ffi.new("double[]", p_number_of_bins)
	for i,v in enumerate(p_dose_bin_width_Gy):
		p_dose_bin_width_Gy__internal[i] = v
	
	p_mean_d_check_Gy__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_mean_d_check_Gy):
		p_mean_d_check_Gy__internal[i] = v
	
	p_sd_d_check_Gy__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_sd_d_check_Gy):
		p_sd_d_check_Gy__internal[i] = v
	
	p_mean_zero_dose_fraction__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_mean_zero_dose_fraction):
		p_mean_zero_dose_fraction__internal[i] = v
	
	p_sd_zero_dose_fraction__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_sd_zero_dose_fraction):
		p_sd_zero_dose_fraction__internal[i] = v
	
	p_mean_dose_frequency_Gy__internal = ffi.new("double[]", p_number_of_bins)
	for i,v in enumerate(p_mean_dose_frequency_Gy):
		p_mean_dose_frequency_Gy__internal[i] = v
	
	p_sd_dose_frequency_Gy__internal = ffi.new("double[]", p_number_of_bins)
	for i,v in enumerate(p_sd_dose_frequency_Gy):
		p_sd_dose_frequency_Gy__internal[i] = v
	
	_libAT.lib.AT_GSM_multiple_local_dose_distrib(p_number_of_field_components__internal.encode() if type(p_number_of_field_components__internal) is str else p_number_of_field_components__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_rdd_model__internal.encode() if type(p_rdd_model__internal) is str else p_rdd_model__internal
			,p_rdd_parameter__internal.encode() if type(p_rdd_parameter__internal) is str else p_rdd_parameter__internal
			,p_er_model__internal.encode() if type(p_er_model__internal) is str else p_er_model__internal
			,p_stopping_power_source_no__internal.encode() if type(p_stopping_power_source_no__internal) is str else p_stopping_power_source_no__internal
			,p_nX__internal.encode() if type(p_nX__internal) is str else p_nX__internal
			,p_pixel_size_m__internal.encode() if type(p_pixel_size_m__internal) is str else p_pixel_size_m__internal
			,p_N_runs__internal.encode() if type(p_N_runs__internal) is str else p_N_runs__internal
			,p_N_repetitions__internal.encode() if type(p_N_repetitions__internal) is str else p_N_repetitions__internal
			,p_number_of_bins__internal.encode() if type(p_number_of_bins__internal) is str else p_number_of_bins__internal
			,p_dose_bin_centers_Gy__internal.encode() if type(p_dose_bin_centers_Gy__internal) is str else p_dose_bin_centers_Gy__internal
			,p_dose_bin_width_Gy__internal.encode() if type(p_dose_bin_width_Gy__internal) is str else p_dose_bin_width_Gy__internal
			,p_mean_d_check_Gy__internal.encode() if type(p_mean_d_check_Gy__internal) is str else p_mean_d_check_Gy__internal
			,p_sd_d_check_Gy__internal.encode() if type(p_sd_d_check_Gy__internal) is str else p_sd_d_check_Gy__internal
			,p_mean_zero_dose_fraction__internal.encode() if type(p_mean_zero_dose_fraction__internal) is str else p_mean_zero_dose_fraction__internal
			,p_sd_zero_dose_fraction__internal.encode() if type(p_sd_zero_dose_fraction__internal) is str else p_sd_zero_dose_fraction__internal
			,p_mean_dose_frequency_Gy__internal.encode() if type(p_mean_dose_frequency_Gy__internal) is str else p_mean_dose_frequency_Gy__internal
			,p_sd_dose_frequency_Gy__internal.encode() if type(p_sd_dose_frequency_Gy__internal) is str else p_sd_dose_frequency_Gy__internal
			)
	for i,v in enumerate(p_dose_bin_width_Gy__internal):
		p_dose_bin_width_Gy[i] = v
	
	for i,v in enumerate(p_mean_d_check_Gy__internal):
		p_mean_d_check_Gy[i] = v
	
	for i,v in enumerate(p_sd_d_check_Gy__internal):
		p_sd_d_check_Gy[i] = v
	
	for i,v in enumerate(p_mean_zero_dose_fraction__internal):
		p_mean_zero_dose_fraction[i] = v
	
	for i,v in enumerate(p_sd_zero_dose_fraction__internal):
		p_sd_zero_dose_fraction[i] = v
	
	for i,v in enumerate(p_mean_dose_frequency_Gy__internal):
		p_mean_dose_frequency_Gy[i] = v
	
	for i,v in enumerate(p_sd_dose_frequency_Gy__internal):
		p_sd_dose_frequency_Gy[i] = v
	
	

def AT_CSDA_range_g_cm2_multi(p_E_initial_MeV_u, p_E_final_MeV_u, p_particle_no, p_material_no, p_CSDA_range_g_cm2):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the CSDA range using the PSTAR data
	@param[in]  	   n                    number of particles
	@param[in]  	   E_initial_MeV_u      initial energy of particle per nucleon (array of size n)
	@param[in]  	   E_final_MeV_u        final energy of particle per nucleon (array of size n)
	@param[in]  	   particle_no  particle index (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[out]    CSDA_range_g_cm2 resulting range (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_initial_MeV_u,p_E_final_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_initial_MeV_u)
	for in_array_argument in [p_E_initial_MeV_u,p_E_final_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_CSDA_range_g_cm2 is passed correctly:
	if len(p_CSDA_range_g_cm2) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_CSDA_range_g_cm2 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_CSDA_range_g_cm2.clear()
		p_CSDA_range_g_cm2 += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_initial_MeV_u)
	p_n__internal = p_n
	p_E_initial_MeV_u__internal = p_E_initial_MeV_u
	p_E_final_MeV_u__internal = p_E_final_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_CSDA_range_g_cm2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_CSDA_range_g_cm2):
		p_CSDA_range_g_cm2__internal[i] = v
	
	_libAT.lib.AT_CSDA_range_g_cm2_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_initial_MeV_u__internal.encode() if type(p_E_initial_MeV_u__internal) is str else p_E_initial_MeV_u__internal
			,p_E_final_MeV_u__internal.encode() if type(p_E_final_MeV_u__internal) is str else p_E_final_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_CSDA_range_g_cm2__internal.encode() if type(p_CSDA_range_g_cm2__internal) is str else p_CSDA_range_g_cm2__internal
			)
	for i,v in enumerate(p_CSDA_range_g_cm2__internal):
		p_CSDA_range_g_cm2[i] = v
	
	

def AT_CSDA_range_g_cm2_single(p_E_initial_MeV_u, p_E_final_MeV_u, p_particle_no, p_material_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the CSDA range using the PSTAR data
	@param[in]  	   E_initial_MeV_u      initial energy of particle per nucleon
	@param[in]  	   E_final_MeV_u       final energy of particle per nucleon
	@param[in]  	   particle_no  particle index
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  material index
	@see          AT_DataMaterial.h for definition
	@return     result
	"""
	p_E_initial_MeV_u__internal = p_E_initial_MeV_u
	p_E_final_MeV_u__internal = p_E_final_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	ret = _libAT.lib.AT_CSDA_range_g_cm2_single(p_E_initial_MeV_u__internal.encode() if type(p_E_initial_MeV_u__internal) is str else p_E_initial_MeV_u__internal
			,p_E_final_MeV_u__internal.encode() if type(p_E_final_MeV_u__internal) is str else p_E_final_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			)
	return ret
	

def AT_CSDA_energy_after_slab_E_MeV_u_single(p_E_initial_MeV_u, p_particle_no, p_material_no, p_slab_thickness_m):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the ion energy after transversing a slab of material using
	the PSTAR data
	@param[in]  	   E_initial_MeV_u      initial energy of particle per nucleon (array of size n)
	@param[in]  	   particle_no          particle index (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]      material_no          material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_m     thickness of slab to transversed
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_initial_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_initial_MeV_u)
	for in_array_argument in [p_E_initial_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_n = len(p_E_initial_MeV_u)
	p_E_initial_MeV_u__internal = p_E_initial_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_m__internal = p_slab_thickness_m
	ret = _libAT.lib.AT_CSDA_energy_after_slab_E_MeV_u_single(p_E_initial_MeV_u__internal.encode() if type(p_E_initial_MeV_u__internal) is str else p_E_initial_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_m__internal.encode() if type(p_slab_thickness_m__internal) is str else p_slab_thickness_m__internal
			)
	return ret
	

def AT_CSDA_energy_after_slab_E_MeV_u_multi(p_E_initial_MeV_u, p_particle_no, p_material_no, p_slab_thickness_m, p_E_final_MeV_u):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the ion energy after transversing a slab of material using Bethe stopping power
	and CSDA approach for many energies / particles
	@param[in]  	   n                    number of particles
	@param[in]  	   E_initial_MeV_u      initial energy of particle per nucleon (array of size n)
	@param[in]  	   particle_no          particle index (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]      material_no          material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_m     thickness of slab to transversed
	@param[out]     E_final_MeV_u        final energy after slab (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_initial_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_initial_MeV_u)
	for in_array_argument in [p_E_initial_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_E_final_MeV_u is passed correctly:
	if len(p_E_final_MeV_u) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_E_final_MeV_u was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_E_final_MeV_u.clear()
		p_E_final_MeV_u += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_initial_MeV_u)
	p_n__internal = p_n
	p_E_initial_MeV_u__internal = p_E_initial_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_m__internal = p_slab_thickness_m
	p_E_final_MeV_u__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_E_final_MeV_u):
		p_E_final_MeV_u__internal[i] = v
	
	_libAT.lib.AT_CSDA_energy_after_slab_E_MeV_u_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_initial_MeV_u__internal.encode() if type(p_E_initial_MeV_u__internal) is str else p_E_initial_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_m__internal.encode() if type(p_slab_thickness_m__internal) is str else p_slab_thickness_m__internal
			,p_E_final_MeV_u__internal.encode() if type(p_E_final_MeV_u__internal) is str else p_E_final_MeV_u__internal
			)
	for i,v in enumerate(p_E_final_MeV_u__internal):
		p_E_final_MeV_u[i] = v
	
	

def AT_WEPL_multi(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_m, p_WEPL):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the water equivalent path length (WEPL) using the Bethe formula
	@param[in]  	   n            number of particles
	@param[in]  	   E_MeV_u      energy of particle per nucleon (array of size n)
	@param[in]  	   particle_no  particle index (array of size n)
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_m  thickness of slab of material different than water, in meter
	@param[out]    WEPL resulting water equivalent path length (array of size n)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_WEPL is passed correctly:
	if len(p_WEPL) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_WEPL was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_WEPL.clear()
		p_WEPL += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_m__internal = p_slab_thickness_m
	p_WEPL__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_WEPL):
		p_WEPL__internal[i] = v
	
	_libAT.lib.AT_WEPL_multi(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_m__internal.encode() if type(p_slab_thickness_m__internal) is str else p_slab_thickness_m__internal
			,p_WEPL__internal.encode() if type(p_WEPL__internal) is str else p_WEPL__internal
			)
	for i,v in enumerate(p_WEPL__internal):
		p_WEPL[i] = v
	
	

def AT_WEPL_single(p_E_MeV_u, p_particle_no, p_material_no, p_slab_thickness_m):
	"""
	Wrapping function generated for C language function documented as follows:
	Computes the water equivalent path length (WEPL) using the Bethe formula
	@param[in]  	   E_MeV_u      energy of particle per nucleon
	@param[in]  	   particle_no  particle index
	@see          AT_DataParticle.h for definition
	@param[in]      material_no  material index
	@see          AT_DataMaterial.h for definition
	@param[in]      slab_thickness_m  thickness of slab of material different than water, in meter
	@return     result
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_slab_thickness_m__internal = p_slab_thickness_m
	ret = _libAT.lib.AT_WEPL_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_slab_thickness_m__internal.encode() if type(p_slab_thickness_m__internal) is str else p_slab_thickness_m__internal
			)
	return ret
	

def AT_SPC_get_number_of_bytes_in_file(p_filename):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in]	filename  	    	path and name for spc file, incl. extension
	@return	    number of bytes in file
	"""
	p_filename__internal = p_filename
	ret = _libAT.lib.AT_SPC_get_number_of_bytes_in_file(p_filename__internal.encode() if type(p_filename__internal) is str else p_filename__internal
			)
	return ret
	

def AT_SPC_get_number_of_bins_from_filename_fast(p_filename):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in]	filename  	    	path and name for spc file, incl. extension
	@return               number of bins
	"""
	p_filename__internal = p_filename
	ret = _libAT.lib.AT_SPC_get_number_of_bins_from_filename_fast(p_filename__internal.encode() if type(p_filename__internal) is str else p_filename__internal
			)
	return ret
	

def AT_SPC_read_header_from_filename_fast(p_filename, p_E_MeV_u, p_peak_position_g_cm2, p_particle_no, p_material_no, p_normalisation, p_depth_steps_no):
	"""
	Wrapping function generated for C language function documented as follows:
	Reads data from spc file into pre-allocated arrays. It will be converted
	for direct use in libamtrack, i.e. to an R-style array of six columns
	(each presented by a single pointer) and all of same length. That of course
	results in redundancy in depth_step, depth_g_cm2, particle_no but enables
	easy division into cells (i.e. passing all spectra of a specific depth and
	particle number to another routine such as total dose). Please note that
	the fluence IS NOT normalized to bin width but given in absolute fluence!
	@param[in]	filename  	    	path and name for spc file, incl. extension
	@param[out]	E_MeV_u			primary beam energy in MeV/u
	@param[out]	peak_position_g_cm2	position of peak in g/cm2
	@param[out]	particle_no         projectile - particle no
	@param[out]	material_no         target - material no
	@param[out]	normalisation		normalisation
	@param[out]  depth_steps_no      number of depth steps
	@return               status code
	"""
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_peak_position_g_cm2,p_particle_no,p_material_no,p_normalisation,p_depth_steps_no]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_peak_position_g_cm2,p_particle_no,p_material_no,p_normalisation,p_depth_steps_no]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_E_MeV_u, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_peak_position_g_cm2, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_particle_no, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_material_no, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_normalisation, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_depth_steps_no, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_E_MeV_u) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_E_MeV_u.clear()
		p_E_MeV_u += [0]
	
	if len(p_peak_position_g_cm2) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_peak_position_g_cm2.clear()
		p_peak_position_g_cm2 += [0]
	
	if len(p_particle_no) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_particle_no.clear()
		p_particle_no += [0]
	
	if len(p_material_no) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_material_no.clear()
		p_material_no += [0]
	
	if len(p_normalisation) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_normalisation.clear()
		p_normalisation += [0]
	
	if len(p_depth_steps_no) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_depth_steps_no.clear()
		p_depth_steps_no += [0]
	
	p_filename__internal = p_filename
	p_E_MeV_u__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_E_MeV_u):
		p_E_MeV_u__internal[i] = v
	
	p_peak_position_g_cm2__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_peak_position_g_cm2):
		p_peak_position_g_cm2__internal[i] = v
	
	p_particle_no__internal = ffi.new("long[]", 1)
	for i,v in enumerate(p_particle_no):
		p_particle_no__internal[i] = v
	
	p_material_no__internal = ffi.new("int[]", 1)
	for i,v in enumerate(p_material_no):
		p_material_no__internal[i] = v
	
	p_normalisation__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_normalisation):
		p_normalisation__internal[i] = v
	
	p_depth_steps_no__internal = ffi.new("int[]", 1)
	for i,v in enumerate(p_depth_steps_no):
		p_depth_steps_no__internal[i] = v
	
	ret = _libAT.lib.AT_SPC_read_header_from_filename_fast(p_filename__internal.encode() if type(p_filename__internal) is str else p_filename__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_peak_position_g_cm2__internal.encode() if type(p_peak_position_g_cm2__internal) is str else p_peak_position_g_cm2__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_normalisation__internal.encode() if type(p_normalisation__internal) is str else p_normalisation__internal
			,p_depth_steps_no__internal.encode() if type(p_depth_steps_no__internal) is str else p_depth_steps_no__internal
			)
	for i,v in enumerate(p_E_MeV_u__internal):
		p_E_MeV_u[i] = v
	
	for i,v in enumerate(p_peak_position_g_cm2__internal):
		p_peak_position_g_cm2[i] = v
	
	for i,v in enumerate(p_particle_no__internal):
		p_particle_no[i] = v
	
	for i,v in enumerate(p_material_no__internal):
		p_material_no[i] = v
	
	for i,v in enumerate(p_normalisation__internal):
		p_normalisation[i] = v
	
	for i,v in enumerate(p_depth_steps_no__internal):
		p_depth_steps_no[i] = v
	
	return ret
	

def AT_SPC_read_data_from_filename_fast(p_filename, p_depth_step, p_depth_g_cm2, p_E_MeV_u, p_DE_MeV_u, p_particle_no, p_fluence_cm2):
	"""
	Wrapping function generated for C language function documented as follows:
	Reads data from spc file into pre-allocated arrays. It will be converted
	for direct use in libamtrack, i.e. to an R-style array of six columns
	(each presented by a single pointer) and all of same length. That of course
	results in redundancy in depth_step, depth_g_cm2, particle_no but enables
	easy division into cells (i.e. passing all spectra of a specific depth and
	particle number to another routine such as total dose). Please note that
	the fluence IS NOT normalized to bin width but given in absolute fluence!
	@param[in]	    filename  	    path and name for spc file, incl. extension
	@param[in]       n               array size, total number of bins expected
	@see AT_SPC_get_size
	@param[out]		depth_step		depth step index, zero-based (array of size n)
	@param[out]		depth_g_cm2		depth in g/cm2 (array of size n)
	@param[out]		E_MeV_u			midpoints of energy bins (array of size n)
	@param[out]		DE_MeV_u		widths of energy bins (array of size n)
	@param[out]		particle_no		particle index numbers (array of size n)
	@param[out]      fluence_cm2		fluence values differential in energy and particle number (array of size n)
	@return                          number of bins read. Must match the array size n
	"""
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_depth_step)
	for in_array_argument in [p_depth_step,p_depth_g_cm2,p_E_MeV_u,p_DE_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_depth_step)
	for in_array_argument in [p_depth_step,p_depth_g_cm2,p_E_MeV_u,p_DE_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_n = len(p_depth_step)
	p_filename__internal = p_filename
	p_n__internal = p_n
	p_depth_step__internal = ffi.new("int[]", p_n)
	for i,v in enumerate(p_depth_step):
		p_depth_step__internal[i] = v
	
	p_depth_g_cm2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_depth_g_cm2):
		p_depth_g_cm2__internal[i] = v
	
	p_E_MeV_u__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_E_MeV_u):
		p_E_MeV_u__internal[i] = v
	
	p_DE_MeV_u__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_DE_MeV_u):
		p_DE_MeV_u__internal[i] = v
	
	p_particle_no__internal = ffi.new("long[]", p_n)
	for i,v in enumerate(p_particle_no):
		p_particle_no__internal[i] = v
	
	p_fluence_cm2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_fluence_cm2):
		p_fluence_cm2__internal[i] = v
	
	ret = _libAT.lib.AT_SPC_read_data_from_filename_fast(p_filename__internal.encode() if type(p_filename__internal) is str else p_filename__internal
			,p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_depth_step__internal.encode() if type(p_depth_step__internal) is str else p_depth_step__internal
			,p_depth_g_cm2__internal.encode() if type(p_depth_g_cm2__internal) is str else p_depth_g_cm2__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_DE_MeV_u__internal.encode() if type(p_DE_MeV_u__internal) is str else p_DE_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			)
	for i,v in enumerate(p_depth_step__internal):
		p_depth_step[i] = v
	
	for i,v in enumerate(p_depth_g_cm2__internal):
		p_depth_g_cm2[i] = v
	
	for i,v in enumerate(p_E_MeV_u__internal):
		p_E_MeV_u[i] = v
	
	for i,v in enumerate(p_DE_MeV_u__internal):
		p_DE_MeV_u[i] = v
	
	for i,v in enumerate(p_particle_no__internal):
		p_particle_no[i] = v
	
	for i,v in enumerate(p_fluence_cm2__internal):
		p_fluence_cm2[i] = v
	
	return ret
	

def AT_SPC_read_from_filename_fast(p_filename, p_E_MeV_u_initial, p_peak_position_g_cm2, p_particle_no_initial, p_material_no, p_normalisation, p_depth_steps_no, p_depth_step, p_depth_g_cm2, p_E_MeV_u, p_DE_MeV_u, p_particle_no, p_fluence_cm2):
	"""
	Wrapping function generated for C language function documented as follows:
	Reads data from spc file into pre-allocated arrays. It will be converted
	for direct use in libamtrack, i.e. to an R-style array of six columns
	(each presented by a single pointer) and all of same length. That of course
	results in redundancy in depth_step, depth_g_cm2, particle_no but enables
	easy division into cells (i.e. passing all spectra of a specific depth and
	particle number to another routine such as total dose). Please note that
	the fluence IS NOT normalized to bin width but given in absolute fluence!
	@param[in]	filename  	    	path and name for spc file, incl. extension
	@param[in]   n                   array size, total number of bins expected
	@see AT_SPC_get_size
	@param[out]	E_MeV_u_initial		primary beam energy in MeV/u
	@param[out]	peak_position_g_cm2	position of peak in g/cm2
	@param[out]	particle_no_initial projectile - particle no
	@param[out]	material_no         target - material no
	@param[out]	normalisation		normalisation
	@param[out]  depth_steps_no      number of depth steps
	@param[out]	depth_step		    depth step index, zero-based (array of size n)
	@param[out]	depth_g_cm2		    depth in g/cm2 (array of size n)
	@param[out]	E_MeV_u			    midpoints of energy bins (array of size n)
	@param[out]	DE_MeV_u		    widths of energy bins (array of size n)
	@param[out]	particle_no		    particle index numbers (array of size n)
	@param[out]  fluence_cm2		    fluence values differential in energy and particle number (array of size n)
	@return                          number of bins read. Must match the array size n
	"""
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_E_MeV_u_initial)
	for in_array_argument in [p_E_MeV_u_initial,p_peak_position_g_cm2,p_particle_no_initial,p_material_no,p_normalisation,p_depth_steps_no]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_depth_step)
	for in_array_argument in [p_depth_step,p_depth_g_cm2,p_E_MeV_u,p_DE_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: 1
	declared_in_arr_param_size__1 = len(p_E_MeV_u_initial)
	for in_array_argument in [p_E_MeV_u_initial,p_peak_position_g_cm2,p_particle_no_initial,p_material_no,p_normalisation,p_depth_steps_no]:
		if len(in_array_argument) != declared_in_arr_param_size__1:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_depth_step)
	for in_array_argument in [p_depth_step,p_depth_g_cm2,p_E_MeV_u,p_DE_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	if not isinstance(p_E_MeV_u_initial, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_peak_position_g_cm2, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_particle_no_initial, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_material_no, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_normalisation, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if not isinstance(p_depth_steps_no, list):
		out_param_err = "You passed OUT parameter not as an array."
		raise ValueError(out_param_err)
	
	if len(p_E_MeV_u_initial) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_E_MeV_u_initial.clear()
		p_E_MeV_u_initial += [0]
	
	if len(p_peak_position_g_cm2) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_peak_position_g_cm2.clear()
		p_peak_position_g_cm2 += [0]
	
	if len(p_particle_no_initial) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_particle_no_initial.clear()
		p_particle_no_initial += [0]
	
	if len(p_material_no) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_material_no.clear()
		p_material_no += [0]
	
	if len(p_normalisation) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_normalisation.clear()
		p_normalisation += [0]
	
	if len(p_depth_steps_no) != 1:
		out_param_auto_init = "\nWarning: OUT parameter (not an array) was passed with incorrect size.\n" + \
			"Wrapper initializes it with size 1"
		warnings.warn(out_param_auto_init)
		p_depth_steps_no.clear()
		p_depth_steps_no += [0]
	
	# Array sizes variables initialization:
	p_n = len(p_depth_step)
	p_filename__internal = p_filename
	p_n__internal = p_n
	p_E_MeV_u_initial__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_E_MeV_u_initial):
		p_E_MeV_u_initial__internal[i] = v
	
	p_peak_position_g_cm2__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_peak_position_g_cm2):
		p_peak_position_g_cm2__internal[i] = v
	
	p_particle_no_initial__internal = ffi.new("long[]", 1)
	for i,v in enumerate(p_particle_no_initial):
		p_particle_no_initial__internal[i] = v
	
	p_material_no__internal = ffi.new("int[]", 1)
	for i,v in enumerate(p_material_no):
		p_material_no__internal[i] = v
	
	p_normalisation__internal = ffi.new("double[]", 1)
	for i,v in enumerate(p_normalisation):
		p_normalisation__internal[i] = v
	
	p_depth_steps_no__internal = ffi.new("int[]", 1)
	for i,v in enumerate(p_depth_steps_no):
		p_depth_steps_no__internal[i] = v
	
	p_depth_step__internal = ffi.new("int[]", p_n)
	for i,v in enumerate(p_depth_step):
		p_depth_step__internal[i] = v
	
	p_depth_g_cm2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_depth_g_cm2):
		p_depth_g_cm2__internal[i] = v
	
	p_E_MeV_u__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_E_MeV_u):
		p_E_MeV_u__internal[i] = v
	
	p_DE_MeV_u__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_DE_MeV_u):
		p_DE_MeV_u__internal[i] = v
	
	p_particle_no__internal = ffi.new("long[]", p_n)
	for i,v in enumerate(p_particle_no):
		p_particle_no__internal[i] = v
	
	p_fluence_cm2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_fluence_cm2):
		p_fluence_cm2__internal[i] = v
	
	ret = _libAT.lib.AT_SPC_read_from_filename_fast(p_filename__internal.encode() if type(p_filename__internal) is str else p_filename__internal
			,p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u_initial__internal.encode() if type(p_E_MeV_u_initial__internal) is str else p_E_MeV_u_initial__internal
			,p_peak_position_g_cm2__internal.encode() if type(p_peak_position_g_cm2__internal) is str else p_peak_position_g_cm2__internal
			,p_particle_no_initial__internal.encode() if type(p_particle_no_initial__internal) is str else p_particle_no_initial__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_normalisation__internal.encode() if type(p_normalisation__internal) is str else p_normalisation__internal
			,p_depth_steps_no__internal.encode() if type(p_depth_steps_no__internal) is str else p_depth_steps_no__internal
			,p_depth_step__internal.encode() if type(p_depth_step__internal) is str else p_depth_step__internal
			,p_depth_g_cm2__internal.encode() if type(p_depth_g_cm2__internal) is str else p_depth_g_cm2__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_DE_MeV_u__internal.encode() if type(p_DE_MeV_u__internal) is str else p_DE_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			)
	for i,v in enumerate(p_E_MeV_u_initial__internal):
		p_E_MeV_u_initial[i] = v
	
	for i,v in enumerate(p_peak_position_g_cm2__internal):
		p_peak_position_g_cm2[i] = v
	
	for i,v in enumerate(p_particle_no_initial__internal):
		p_particle_no_initial[i] = v
	
	for i,v in enumerate(p_material_no__internal):
		p_material_no[i] = v
	
	for i,v in enumerate(p_normalisation__internal):
		p_normalisation[i] = v
	
	for i,v in enumerate(p_depth_steps_no__internal):
		p_depth_steps_no[i] = v
	
	for i,v in enumerate(p_depth_step__internal):
		p_depth_step[i] = v
	
	for i,v in enumerate(p_depth_g_cm2__internal):
		p_depth_g_cm2[i] = v
	
	for i,v in enumerate(p_E_MeV_u__internal):
		p_E_MeV_u[i] = v
	
	for i,v in enumerate(p_DE_MeV_u__internal):
		p_DE_MeV_u[i] = v
	
	for i,v in enumerate(p_particle_no__internal):
		p_particle_no[i] = v
	
	for i,v in enumerate(p_fluence_cm2__internal):
		p_fluence_cm2[i] = v
	
	return ret
	

def AT_SPC_number_of_bins_at_range(p_path, p_range_g_cm2):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in]   path            	path to spc file dir (array of size 2048)
	@param[in]   range_g_cm2         range in g/cm2
	@return                          number of bins for given range
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_path]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	p_path__internal = p_path
	p_range_g_cm2__internal = p_range_g_cm2
	ret = _libAT.lib.AT_SPC_number_of_bins_at_range(p_path__internal.encode() if type(p_path__internal) is str else p_path__internal
			,p_range_g_cm2__internal.encode() if type(p_range_g_cm2__internal) is str else p_range_g_cm2__internal
			)
	return ret
	

def AT_SPC_spectrum_at_range(p_path, p_range_g_cm2, p_depth_step, p_depth_g_cm2, p_E_MeV_u, p_DE_MeV_u, p_particle_no, p_fluence_cm2):
	"""
	Wrapping function generated for C language function documented as follows:
	TODO
	@param[in]   path            	path to spc file dir (array of size 2048)
	@param[in]   range_g_cm2         range in g/cm2
	@param[in]   n                   array size, total number of bins expected
	@param[out]	depth_step		    depth step index, zero-based (array of size n)
	@param[out]	depth_g_cm2		    depth in g/cm2 (array of size n)
	@param[out]	E_MeV_u			    midpoints of energy bins (array of size n)
	@param[out]	DE_MeV_u		    widths of energy bins (array of size n)
	@param[out]	particle_no		    particle index numbers (array of size n)
	@param[out]  fluence_cm2		    fluence values differential in energy and particle number (array of size n)
	@return                          status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_path]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every OUT array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_depth_step)
	for in_array_argument in [p_depth_step,p_depth_g_cm2,p_E_MeV_u,p_DE_MeV_u,p_particle_no,p_fluence_cm2]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Array sizes variables initialization:
	p_n = len(p_depth_step)
	p_path__internal = p_path
	p_range_g_cm2__internal = p_range_g_cm2
	p_n__internal = p_n
	p_depth_step__internal = ffi.new("int[]", p_n)
	for i,v in enumerate(p_depth_step):
		p_depth_step__internal[i] = v
	
	p_depth_g_cm2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_depth_g_cm2):
		p_depth_g_cm2__internal[i] = v
	
	p_E_MeV_u__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_E_MeV_u):
		p_E_MeV_u__internal[i] = v
	
	p_DE_MeV_u__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_DE_MeV_u):
		p_DE_MeV_u__internal[i] = v
	
	p_particle_no__internal = ffi.new("long[]", p_n)
	for i,v in enumerate(p_particle_no):
		p_particle_no__internal[i] = v
	
	p_fluence_cm2__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_fluence_cm2):
		p_fluence_cm2__internal[i] = v
	
	ret = _libAT.lib.AT_SPC_spectrum_at_range(p_path__internal.encode() if type(p_path__internal) is str else p_path__internal
			,p_range_g_cm2__internal.encode() if type(p_range_g_cm2__internal) is str else p_range_g_cm2__internal
			,p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_depth_step__internal.encode() if type(p_depth_step__internal) is str else p_depth_step__internal
			,p_depth_g_cm2__internal.encode() if type(p_depth_g_cm2__internal) is str else p_depth_g_cm2__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_DE_MeV_u__internal.encode() if type(p_DE_MeV_u__internal) is str else p_DE_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_fluence_cm2__internal.encode() if type(p_fluence_cm2__internal) is str else p_fluence_cm2__internal
			)
	for i,v in enumerate(p_depth_step__internal):
		p_depth_step[i] = v
	
	for i,v in enumerate(p_depth_g_cm2__internal):
		p_depth_g_cm2[i] = v
	
	for i,v in enumerate(p_E_MeV_u__internal):
		p_E_MeV_u[i] = v
	
	for i,v in enumerate(p_DE_MeV_u__internal):
		p_DE_MeV_u[i] = v
	
	for i,v in enumerate(p_particle_no__internal):
		p_particle_no[i] = v
	
	for i,v in enumerate(p_fluence_cm2__internal):
		p_fluence_cm2[i] = v
	
	return ret
	

def AT_ICRU_wrapper(p_E_MeV_u, p_particle_no, p_material_no, p_info, p_mass_stopping_power_MeV_cm2_g):
	"""
	Wrapping function generated for C language function documented as follows:
	@brief Stopping power
	Returns the electronic mass stopping power in MeV*cm2/g
	as given by ICRU49 (H+He) and ICRU 73 (Li...Ar). The data
	have be transformed to fit the units (E/u and MeV*cm2/g).
	@param[in]   n							    number of energies / particles
	@param[in]   E_MeV_u					    	kinetic energies in MeV per amu (array of size n)
	@param[in]   particle_no                     particle numbers (array of size n)
	@param[in]   material_no                 	material number
	@param[in]   info							not used
	@param[out]  mass_stopping_power_MeV_cm2_g   array to return stopping powers (array of size n)
	@return
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_no]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_mass_stopping_power_MeV_cm2_g is passed correctly:
	if len(p_mass_stopping_power_MeV_cm2_g) != len(p_particle_no):
		out_array_auto_init = "\nWarning: OUT array parameter p_mass_stopping_power_MeV_cm2_g was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_mass_stopping_power_MeV_cm2_g.clear()
		p_mass_stopping_power_MeV_cm2_g += [0]*len(p_particle_no)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_no__internal = p_particle_no
	p_material_no__internal = p_material_no
	p_info__internal = p_info
	p_mass_stopping_power_MeV_cm2_g__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_mass_stopping_power_MeV_cm2_g):
		p_mass_stopping_power_MeV_cm2_g__internal[i] = v
	
	ret = _libAT.lib.AT_ICRU_wrapper(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_no__internal.encode() if type(p_particle_no__internal) is str else p_particle_no__internal
			,p_material_no__internal.encode() if type(p_material_no__internal) is str else p_material_no__internal
			,p_info__internal.encode() if type(p_info__internal) is str else p_info__internal
			,p_mass_stopping_power_MeV_cm2_g__internal.encode() if type(p_mass_stopping_power_MeV_cm2_g__internal) is str else p_mass_stopping_power_MeV_cm2_g__internal
			)
	for i,v in enumerate(p_mass_stopping_power_MeV_cm2_g__internal):
		p_mass_stopping_power_MeV_cm2_g[i] = v
	
	return ret
	

def AT_characteristic_single_scattering_angle_single(p_E_MeV_u, p_particle_charge_e, p_target_thickness_cm, p_element_acronym):
	"""
	Wrapping function generated for C language function documented as follows:
	@brief Moliere theory of multiple Coulomb scattering
	Returns characteristic single scattering angle chi_c
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV]
	@param[in]  particle_charge_e    	charge number of particle
	@param[in]  target_thickness_cm      thickness of the target material in cm
	@param[in]  element_acronym		    elemental symbol of target material (array of size PARTICLE_NAME_NCHAR)
	@return     chi_c in rad
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_element_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Array sizes variables initialization:
	p_PARTICLE_NAME_NCHAR = len(p_element_acronym)
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	p_target_thickness_cm__internal = p_target_thickness_cm
	p_element_acronym__internal = p_element_acronym
	ret = _libAT.lib.AT_characteristic_single_scattering_angle_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_target_thickness_cm__internal.encode() if type(p_target_thickness_cm__internal) is str else p_target_thickness_cm__internal
			,p_element_acronym__internal.encode() if type(p_element_acronym__internal) is str else p_element_acronym__internal
			)
	return ret
	

def AT_characteristic_single_scattering_angle(p_E_MeV_u, p_particle_charge_e, p_target_thickness_cm, p_element_acronym, p_chi_c):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns characteristic single scattering angles chi_c
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  vector of energies of particle per nucleon [MeV] (array of size n)
	@param[in]  particle_charge_e    	vector of charge numbers of particle (array of size n)
	@param[in]  target_thickness_cm      vector of thicknesses of target material in cm (array of size n)
	@param[in]  element_acronym		    vector of elemental symbols of target material (array of size n)
	@param[out] chi_c                    vector of characteristic single scattering angles in rad (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_charge_e,p_target_thickness_cm,p_element_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_charge_e,p_target_thickness_cm,p_element_acronym]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_chi_c is passed correctly:
	if len(p_chi_c) != len(p_element_acronym):
		out_array_auto_init = "\nWarning: OUT array parameter p_chi_c was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_chi_c.clear()
		p_chi_c += [0]*len(p_element_acronym)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	p_target_thickness_cm__internal = p_target_thickness_cm
	arg_keepalive = [ffi.new("char[]", x.encode() if type(x) is str else x) for x in p_element_acronym]
	p_element_acronym__internal = ffi.new("char* []", arg_keepalive)
	p_chi_c__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_chi_c):
		p_chi_c__internal[i] = v
	
	ret = _libAT.lib.AT_characteristic_single_scattering_angle(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_target_thickness_cm__internal.encode() if type(p_target_thickness_cm__internal) is str else p_target_thickness_cm__internal
			,p_element_acronym__internal.encode() if type(p_element_acronym__internal) is str else p_element_acronym__internal
			,p_chi_c__internal.encode() if type(p_chi_c__internal) is str else p_chi_c__internal
			)
	for i,v in enumerate(p_chi_c__internal):
		p_chi_c[i] = v
	
	return ret
	

def AT_screening_angle_single(p_E_MeV_u, p_particle_charge_e, p_element_acronym):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns screening angle chi_a
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV]
	@param[in]  particle_charge_e    	charge number of particle
	@param[in]  element_acronym		    elemental symbol of target material (array of size PARTICLE_NAME_NCHAR)
	@return     chi_a in rad
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_element_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Array sizes variables initialization:
	p_PARTICLE_NAME_NCHAR = len(p_element_acronym)
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	p_element_acronym__internal = p_element_acronym
	ret = _libAT.lib.AT_screening_angle_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_element_acronym__internal.encode() if type(p_element_acronym__internal) is str else p_element_acronym__internal
			)
	return ret
	

def AT_screening_angle(p_E_MeV_u, p_particle_charge_e, p_element_acronym, p_chi_a):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns screening angles chi_a
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  vector of energies of particle per nucleon [MeV] (array of size n)
	@param[in]  particle_charge_e    	vector of charge numbers of particle (array of size n)
	@param[in]  element_acronym		    vector of elemental symbols of target material (array of size n)
	@param[out] chi_a                    vector of screening angles in rad (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_charge_e,p_element_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_charge_e,p_element_acronym]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_chi_a is passed correctly:
	if len(p_chi_a) != len(p_element_acronym):
		out_array_auto_init = "\nWarning: OUT array parameter p_chi_a was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_chi_a.clear()
		p_chi_a += [0]*len(p_element_acronym)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	arg_keepalive = [ffi.new("char[]", x.encode() if type(x) is str else x) for x in p_element_acronym]
	p_element_acronym__internal = ffi.new("char* []", arg_keepalive)
	p_chi_a__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_chi_a):
		p_chi_a__internal[i] = v
	
	ret = _libAT.lib.AT_screening_angle(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_element_acronym__internal.encode() if type(p_element_acronym__internal) is str else p_element_acronym__internal
			,p_chi_a__internal.encode() if type(p_chi_a__internal) is str else p_chi_a__internal
			)
	for i,v in enumerate(p_chi_a__internal):
		p_chi_a[i] = v
	
	return ret
	

def AT_effective_collision_number_single(p_E_MeV_u, p_particle_charge_e, p_target_thickness_cm, p_element_acronym):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns effective collision number exp_b
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV]
	@param[in]  particle_charge_e    	charge number of particle
	@param[in]  target_thickness_cm      thickness of the target material in cm
	@param[in]  element_acronym		    elemental symbol of target material (array of size PARTICLE_NAME_NCHAR)
	@return     exp_b
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_element_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Array sizes variables initialization:
	p_PARTICLE_NAME_NCHAR = len(p_element_acronym)
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	p_target_thickness_cm__internal = p_target_thickness_cm
	p_element_acronym__internal = p_element_acronym
	ret = _libAT.lib.AT_effective_collision_number_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_target_thickness_cm__internal.encode() if type(p_target_thickness_cm__internal) is str else p_target_thickness_cm__internal
			,p_element_acronym__internal.encode() if type(p_element_acronym__internal) is str else p_element_acronym__internal
			)
	return ret
	

def AT_effective_collision_number(p_E_MeV_u, p_particle_charge_e, p_target_thickness_cm, p_element_acronym, p_exp_b):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns effective collision numbers exp_b
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  vector of energies of particle per nucleon [MeV] (array of size n)
	@param[in]  particle_charge_e    	vector of charge numbers of particle (array of size n)
	@param[in]  target_thickness_cm      vector of thicknesses of target material in cm (array of size n)
	@param[in]  element_acronym		    vector of elemental symbols of target material (array of size n)
	@param[out] exp_b	                vector of effective collision numbers (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_charge_e,p_target_thickness_cm,p_element_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_charge_e,p_target_thickness_cm,p_element_acronym]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_exp_b is passed correctly:
	if len(p_exp_b) != len(p_element_acronym):
		out_array_auto_init = "\nWarning: OUT array parameter p_exp_b was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_exp_b.clear()
		p_exp_b += [0]*len(p_element_acronym)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	p_target_thickness_cm__internal = p_target_thickness_cm
	arg_keepalive = [ffi.new("char[]", x.encode() if type(x) is str else x) for x in p_element_acronym]
	p_element_acronym__internal = ffi.new("char* []", arg_keepalive)
	p_exp_b__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_exp_b):
		p_exp_b__internal[i] = v
	
	ret = _libAT.lib.AT_effective_collision_number(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_target_thickness_cm__internal.encode() if type(p_target_thickness_cm__internal) is str else p_target_thickness_cm__internal
			,p_element_acronym__internal.encode() if type(p_element_acronym__internal) is str else p_element_acronym__internal
			,p_exp_b__internal.encode() if type(p_exp_b__internal) is str else p_exp_b__internal
			)
	for i,v in enumerate(p_exp_b__internal):
		p_exp_b[i] = v
	
	return ret
	

def AT_characteristic_multiple_scattering_angle_single(p_E_MeV_u, p_particle_charge_e, p_target_thickness_cm, p_element_acronym):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns characteristic multiple scattering angle Theta_M
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV]
	@param[in]  particle_charge_e    	charge number of particle
	@param[in]  target_thickness_cm      thickness of the target material in cm
	@param[in]  element_acronym		    elemental symbol of target material (array of size PARTICLE_NAME_NCHAR)
	@return     Theta_M in rad
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_element_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Array sizes variables initialization:
	p_PARTICLE_NAME_NCHAR = len(p_element_acronym)
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	p_target_thickness_cm__internal = p_target_thickness_cm
	p_element_acronym__internal = p_element_acronym
	ret = _libAT.lib.AT_characteristic_multiple_scattering_angle_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_target_thickness_cm__internal.encode() if type(p_target_thickness_cm__internal) is str else p_target_thickness_cm__internal
			,p_element_acronym__internal.encode() if type(p_element_acronym__internal) is str else p_element_acronym__internal
			)
	return ret
	

def AT_characteristic_multiple_scattering_angle(p_E_MeV_u, p_particle_charge_e, p_target_thickness_cm, p_element_acronym, p_Theta_M):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns characteristic multiple scattering angles Theta_M
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  vector of energies of particle per nucleon [MeV] (array of size n)
	@param[in]  particle_charge_e    	vector of charge numbers of particle (array of size n)
	@param[in]  target_thickness_cm      vector of thicknesses of target material in cm (array of size n)
	@param[in]  element_acronym		    vector of elemental symbols of target material (array of size n)
	@param[out] Theta_M		            vector of characteristic multiple scattering angles in rad (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_charge_e,p_target_thickness_cm,p_element_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_charge_e,p_target_thickness_cm,p_element_acronym]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_Theta_M is passed correctly:
	if len(p_Theta_M) != len(p_element_acronym):
		out_array_auto_init = "\nWarning: OUT array parameter p_Theta_M was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_Theta_M.clear()
		p_Theta_M += [0]*len(p_element_acronym)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	p_target_thickness_cm__internal = p_target_thickness_cm
	arg_keepalive = [ffi.new("char[]", x.encode() if type(x) is str else x) for x in p_element_acronym]
	p_element_acronym__internal = ffi.new("char* []", arg_keepalive)
	p_Theta_M__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_Theta_M):
		p_Theta_M__internal[i] = v
	
	ret = _libAT.lib.AT_characteristic_multiple_scattering_angle(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_target_thickness_cm__internal.encode() if type(p_target_thickness_cm__internal) is str else p_target_thickness_cm__internal
			,p_element_acronym__internal.encode() if type(p_element_acronym__internal) is str else p_element_acronym__internal
			,p_Theta_M__internal.encode() if type(p_Theta_M__internal) is str else p_Theta_M__internal
			)
	for i,v in enumerate(p_Theta_M__internal):
		p_Theta_M[i] = v
	
	return ret
	

def AT_scattering_angle_distribution_single(p_E_MeV_u, p_particle_charge_e, p_target_thickness_cm, p_element_acronym, p_Theta):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns scattering angle distribution f(Theta)
	The distribution is not normalized because the energy loss in the target is not considered.
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV]
	@param[in]  particle_charge_e    	charge number of particle
	@param[in]  target_thickness_cm      thickness of the target material in cm
	@param[in]  element_acronym		    elemental symbol of target material (array of size PARTICLE_NAME_NCHAR)
	@param[in]  Theta				   	polar angle in rad
	@return     f(Theta)
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_element_acronym]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Array sizes variables initialization:
	p_PARTICLE_NAME_NCHAR = len(p_element_acronym)
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	p_target_thickness_cm__internal = p_target_thickness_cm
	p_element_acronym__internal = p_element_acronym
	p_Theta__internal = p_Theta
	ret = _libAT.lib.AT_scattering_angle_distribution_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_target_thickness_cm__internal.encode() if type(p_target_thickness_cm__internal) is str else p_target_thickness_cm__internal
			,p_element_acronym__internal.encode() if type(p_element_acronym__internal) is str else p_element_acronym__internal
			,p_Theta__internal.encode() if type(p_Theta__internal) is str else p_Theta__internal
			)
	return ret
	

def AT_scattering_angle_distribution(p_E_MeV_u, p_particle_charge_e, p_target_thickness_cm, p_element_acronym, p_Theta, p_distribution):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns scattering angle distribution f(Theta)
	The distribution is not normalized because the energy loss in the target is not considered.
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV]
	@param[in]  particle_charge_e    	charge number of particle
	@param[in]  target_thickness_cm      thickness of the target material in cm
	@param[in]  element_acronym		    elemental symbol of target material (array of size PARTICLE_NAME_NCHAR)
	@param[in]  Theta				   	vector of polar angles in rad (array of size n)
	@param[out] distribution		        vector of scattering angle distribution values (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_element_acronym,p_Theta]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if OUT array p_distribution is passed correctly:
	if len(p_distribution) != len(p_Theta):
		out_array_auto_init = "\nWarning: OUT array parameter p_distribution was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_distribution.clear()
		p_distribution += [0]*len(p_Theta)
	
	# Array sizes variables initialization:
	p_PARTICLE_NAME_NCHAR = len(p_element_acronym)
	p_n = len(p_Theta)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	p_target_thickness_cm__internal = p_target_thickness_cm
	p_element_acronym__internal = p_element_acronym
	p_Theta__internal = p_Theta
	p_distribution__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_distribution):
		p_distribution__internal[i] = v
	
	ret = _libAT.lib.AT_scattering_angle_distribution(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_target_thickness_cm__internal.encode() if type(p_target_thickness_cm__internal) is str else p_target_thickness_cm__internal
			,p_element_acronym__internal.encode() if type(p_element_acronym__internal) is str else p_element_acronym__internal
			,p_Theta__internal.encode() if type(p_Theta__internal) is str else p_Theta__internal
			,p_distribution__internal.encode() if type(p_distribution__internal) is str else p_distribution__internal
			)
	for i,v in enumerate(p_distribution__internal):
		p_distribution[i] = v
	
	return ret
	

def AT_Highland_angle_single(p_E_MeV_u, p_particle_charge_e, p_l_over_lR):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns Highland angle Theta0
	@param[in]  E_MeV_u                  energy of particle per nucleon [MeV]
	@param[in]  particle_charge_e    	charge number of particle
	@param[in]  l_over_lR     			thickness of the target material in radiation lengths
	@return     Theta0 in rad
	"""
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	p_l_over_lR__internal = p_l_over_lR
	ret = _libAT.lib.AT_Highland_angle_single(p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_l_over_lR__internal.encode() if type(p_l_over_lR__internal) is str else p_l_over_lR__internal
			)
	return ret
	

def AT_Highland_angle(p_E_MeV_u, p_particle_charge_e, p_l_over_lR, p_Theta0):
	"""
	Wrapping function generated for C language function documented as follows:
	Returns Highland angles Theta0
	@param[in]  n                        number of particles
	@param[in]  E_MeV_u                  vector of energies of particle per nucleon [MeV] (array of size n)
	@param[in]  particle_charge_e    	vector of charge numbers of particle (array of size n)
	@param[in]  l_over_lR		        vector of thicknesses of target material in radiation lengths (array of size n)
	@param[out] Theta0		            vector of Highland angles in rad (array of size n)
	@return     status code
	"""
	# Procedure to check if an IN array is empty:
	for in_array_argument in [p_E_MeV_u,p_particle_charge_e,p_l_over_lR]:
		if not in_array_argument:
			warnings.warn("You passed an empty list as an IN parameter.")
	
	# Procedure to check if every IN array of the same declared size, has indeed same size:
	# For arrays of declared size: n
	declared_in_arr_param_size__n = len(p_E_MeV_u)
	for in_array_argument in [p_E_MeV_u,p_particle_charge_e,p_l_over_lR]:
		if len(in_array_argument) != declared_in_arr_param_size__n:
			raise ValueError("You passed as parameters two or more lists that should have the same size, with different sizes.")
	
	# Procedure to check if OUT array p_Theta0 is passed correctly:
	if len(p_Theta0) != len(p_l_over_lR):
		out_array_auto_init = "\nWarning: OUT array parameter p_Theta0 was passed with incorrect size.\n" + \
			"Wrapper initializes it with a correct value based on an IN array parameter of the same declared size"
		warnings.warn(out_array_auto_init)
		p_Theta0.clear()
		p_Theta0 += [0]*len(p_l_over_lR)
	
	# Array sizes variables initialization:
	p_n = len(p_E_MeV_u)
	p_n__internal = p_n
	p_E_MeV_u__internal = p_E_MeV_u
	p_particle_charge_e__internal = p_particle_charge_e
	p_l_over_lR__internal = p_l_over_lR
	p_Theta0__internal = ffi.new("double[]", p_n)
	for i,v in enumerate(p_Theta0):
		p_Theta0__internal[i] = v
	
	ret = _libAT.lib.AT_Highland_angle(p_n__internal.encode() if type(p_n__internal) is str else p_n__internal
			,p_E_MeV_u__internal.encode() if type(p_E_MeV_u__internal) is str else p_E_MeV_u__internal
			,p_particle_charge_e__internal.encode() if type(p_particle_charge_e__internal) is str else p_particle_charge_e__internal
			,p_l_over_lR__internal.encode() if type(p_l_over_lR__internal) is str else p_l_over_lR__internal
			,p_Theta0__internal.encode() if type(p_Theta0__internal) is str else p_Theta0__internal
			)
	for i,v in enumerate(p_Theta0__internal):
		p_Theta0[i] = v
	
	return ret
	

