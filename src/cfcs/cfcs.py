import sublime
import os
from .. import model_index
from .. import utils

projects = {}

def build_project_cfcs(project_name):
	cfc_index = {}
	cfc_folders = model_index.get_project_data(project_name).get("cfc_folders", [])
	for cfc_folder in cfc_folders:
		if cfc_folder.get("variable_names", []):
			accessors = cfc_folder.get("accessors", True)
			if not isinstance(accessors, bool):
				accessors = True
			cfc_index.update(build_cfcs(cfc_folder["path"], cfc_folder["variable_names"], accessors, project_name))
	projects[project_name] = cfc_index

def build_cfcs(root_path, cfc_names, accessors, project_name):
	folder_cfc_index = {}
	for file_path in model_index.get_file_paths(project_name):
		for cfc_name in get_cfc_names(root_path, cfc_names, project_name, file_path):
			folder_cfc_index[cfc_name.lower()] = {"name": cfc_name, "file_path": file_path, "accessors": accessors}
	return folder_cfc_index

def get_cfc_names(root_path, cfc_names, project_name, file_path):
	cfc_path, file_ext = os.path.splitext(file_path)
	cfc_path_parts = utils.normalize_path(cfc_path).replace(utils.normalize_path(root_path), "").split("/")
	metadata = model_index.get_metadata_by_file_path(project_name, file_path)
	path_keys = {}
	path_keys["cfc"] = cfc_path_parts[-1]
	path_keys["entity_name"] = metadata["entityname"] if metadata["entityname"] else path_keys["cfc"]
	path_keys["cfc_folder"] = uppercase(cfc_path_parts[-2])
	path_keys["cfc_folder_singularized"] = path_keys["cfc_folder"] if len(path_keys["cfc_folder"]) == 0 or path_keys["cfc_folder"][-1] != "s" else path_keys["cfc_folder"][:-1]
	return [get_cfc_name(cfc_name, path_keys) for cfc_name in cfc_names]

def get_cfc_name(cfc_name, path_keys):
	for path_key in path_keys:
		cfc_name = cfc_name.replace("{" + path_key + "}", path_keys[path_key])
	return cfc_name

def get_cfc_list(project_name):
	if project_name in projects:
		return [projects[project_name][key]["name"] for key in sorted(projects[project_name])]
	return []

def has_cfc(project_name, cfc_name):
	if project_name in projects:
		return cfc_name.lower() in projects[project_name]
	return False

def search_dot_context_for_cfc(project_name, dot_context):
	stack = []
	regions = []
	for symbol in dot_context:
		if not symbol.is_function:
			stack.append(symbol.name)
			regions.append(symbol.name_region)
		else:
			if len(stack) > 0:
				break

	if len(stack) > 0:
		stack.reverse()
		regions.reverse()
		for i in range(len(stack)):
			cfc_name = ".".join(stack[i:])
			if has_cfc(project_name, cfc_name):
				return cfc_name, sublime.Region(regions[i].begin(), regions[-1].end())
	return None, None

def get_cfc_info(project_name, cfc_name):
	return projects[project_name][cfc_name.lower()]

def get_cfc_completions(project_name, cfc_name):
	cfc_info = get_cfc_info(project_name, cfc_name)
	cfc_completions = model_index.get_completions_by_file_path(project_name, cfc_info["file_path"])["functions"]
	return [get_completion(completion, cfc_info) for completion in cfc_completions if cfc_info["accessors"] or not completion.accessor]

def get_cfc_metadata(project_name, cfc_name):
	file_path = get_cfc_info(project_name, cfc_name)["file_path"]
	return model_index.get_extended_metadata_by_file_path(project_name, file_path)

def get_completion(completion, cfc_info):
	hint = cfc_info["name"]
	if cfc_info["file_path"] != completion.file_path:
		hint = completion.file_path.split("/").pop()
	return completion.key + "\t" + hint, completion.content

def uppercase(string):
	if len(string) == 0:
		return ""
	return string[0].upper() + string[1:]

