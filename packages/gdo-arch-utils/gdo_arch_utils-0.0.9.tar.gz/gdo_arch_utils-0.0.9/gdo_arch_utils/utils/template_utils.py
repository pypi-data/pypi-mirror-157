from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class TemplateUtils:

	@staticmethod
	def _replace_keys_with_values(template_str, values_dict):
		for key, value in values_dict.items():
			template_str = template_str.replace(key, value)
		return template_str

	@staticmethod
	def get_template_with_replaced_values(template_path, values_dict):
		with open(template_path) as f:
			template_content = f.read()
		return TemplateUtils._replace_keys_with_values(template_content, values_dict)
