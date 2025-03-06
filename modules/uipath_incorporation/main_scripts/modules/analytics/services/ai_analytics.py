import logging
import pandas as pd
import re
import os
from modules.analytics.models.ai_files_analytics_model import AiFilesAnalyticsModel
from modules.analytics.models.ai_agent_analytics_model import AiAgentAnalyticsModel

class AiAnalytics:
    ai_files_analytics: AiFilesAnalyticsModel = AiFilesAnalyticsModel()

    @staticmethod
    def add_file_agent_request(
        file_name: str,
        agent_name: str,
        ai_model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        execution_time_in_seconds: float,
        extra_info: str = None,
        log: bool = False,
    ) -> None:
        """
        Adds an AI Agent Analytics Model to the list of agent requests.

        Args:
            file_name (str): The name of the file.
            agent_name (str): The name of the agent.
            ai_model (str): The AI model.
            prompt_tokens (int): The number of tokens in the prompt.
            completion_tokens (int): The number of tokens in the completion.
            total_tokens (int): The total number of tokens.
            execution_time_in_seconds (float): The execution time.
            extra_info (str, optional): Extra information. Defaults to None.
        """
        agent_request = AiAgentAnalyticsModel(
            name=agent_name,
            ai_model=ai_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            execution_time_in_seconds=execution_time_in_seconds,
            extra_info=extra_info,
        )

        AiAnalytics.ai_files_analytics.add_agent_request(file_name, agent_request)

        if log:
            logging.info(f"Added agent request: {agent_request}")

    @staticmethod
    def export_str_ai_analytics_data_to_excel(
        data: str = None,
        output_file_path: str = f"./assets/ai_analytics/{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}_ai_analytics.xlsx",
    ) -> None:
        """
        Exports the AI Analytics to an Excel file.

        Args:
            data (str, optional): The data to be exported. Defaults to None.
            output_file_path (str): The output file path. Defaults to a timestamped path.
        """
        data = data if data else str(AiAnalytics.ai_files_analytics)
        if not data or "#####" not in data:
            raise ValueError("O formato do texto fornecido não é válido. Verifique os delimitadores '#####'.")

        # Configurações fixas para o Excel
        constants = {
            "1 Million Tokens": 1000000,
        }
        pricings = {
            "gpt-4o-mini-2024-07-18": {
                "Pricing Input per 1M Tokens": 0.15,
                "Pricing Output per 1M Tokens": 0.6,
            },
            "gpt-4o-mini": {
                "Pricing Input per 1M Tokens": 0.15,
                "Pricing Output per 1M Tokens": 0.6,
            },
            "gpt-4o": {
                "Pricing Input per 1M Tokens": 2.5,
                "Pricing Output per 1M Tokens": 10,
            },
            "gpt-4o-mini_fine-tuning": {
                "Pricing Input per 1M Tokens": 0.3,
                "Pricing Output per 1M Tokens": 1.2,
            },
            "gpt-4o_fine-tuning": {
                "Pricing Input per 1M Tokens": 3.75,
                "Pricing Output per 1M Tokens": 15,
            },
        }

        # Função para processar os dados
        def process_data_per_section(raw_section: str) -> list[dict[str, any]]:
            try:
                section_lines = raw_section.strip().split("\n")
                section_title = section_lines[0].strip()
                file_name, total_duration = map(str.strip, section_title.split(" - Demorou "))
                data_lines = section_lines[1:]
                rows = []

                for line in data_lines:
                    match = re.search(
                        r"(\w+\s*(?:\([^)]+\))?)\s*- ai_model=([a-zA-Z0-9_\-:.]+)\s+CompletionUsage\(prompt_tokens=(\d+),\s+completion_tokens=(\d+),\s+total_tokens=(\d+)\)\s+- Demorou\s+([\d\.]+s)",
                        line,
                    )
                    if not match:
                        continue

                    agent, ai_model, prompt_tokens, completion_tokens, total_tokens, duration = match.groups()
                    ai_model_for_pricing_calcs = None

                    if ai_model in pricings:
                        model_type = "base-model"
                        ai_model_for_pricing_calcs = ai_model
                    elif ai_model.startswith("ft:"):
                        # OpenAI Example: ft:gpt-4o-mini-2024-07-18:inspireit::ApwmDPft
                        model_type = "ft"
                        base_model_used = ai_model.split(":")[1]  # gpt-4o-mini-2024-07-18
                        components = base_model_used.split("-")
                        try:
                            base_model = "-".join(components[:-3]) # -3 = Exclude the api_version date
                        except ValueError:
                            model_type = None
                            base_model = None
                    else:
                        # Azure Example: gpt-4o-mini-2024-07-18-ft-bf955afee8a8468d90d7a50a5887c450
                        components = ai_model.split("-")
                        try:
                            ft_index = components.index("ft")
                            model_type = components[ft_index]
                            base_model = "-".join(components[:ft_index - 3])  # -3 = Exclude the api_version date
                        except ValueError:
                            model_type = None
                            base_model = None

                    # Check if type is 'ft' (fine-tuning)
                    if model_type == "ft":
                        fine_tuning_key = f"{base_model}_fine-tuning"
                        ai_model_for_pricing_calcs = fine_tuning_key if fine_tuning_key in pricings else None

                    if ai_model_for_pricing_calcs is None:
                        raise ValueError(f"O modelo AI '{ai_model}' convertido para a key '{ai_model_for_pricing_calcs}' não foi encontrado nas configurações de preços.")

                    prompt_tokens_cost = int(prompt_tokens) * pricings[ai_model_for_pricing_calcs]["Pricing Input per 1M Tokens"] / constants["1 Million Tokens"]
                    completion_tokens_cost = int(completion_tokens) * pricings[ai_model_for_pricing_calcs]["Pricing Output per 1M Tokens"] / constants["1 Million Tokens"]
                    total_tokens_cost = prompt_tokens_cost + completion_tokens_cost

                    rows.append({
                        "File": file_name,
                        "Agent": agent,
                        "AI Model": ai_model if ai_model == ai_model_for_pricing_calcs else f"{ai_model} ({ai_model_for_pricing_calcs})",
                        "prompt_tokens used": int(prompt_tokens),
                        "prompt_tokens cost": prompt_tokens_cost,
                        "completion_tokens used": int(completion_tokens),
                        "completion_tokens cost": completion_tokens_cost,
                        "total_tokens used": int(total_tokens),
                        "total_tokens cost": total_tokens_cost,
                        "Duration": duration,
                        "Average Duration": "-",
                    })
                
                # Calcular totais por Agent
                for agent in set(row["Agent"] for row in rows):
                    agent_rows = [row for row in rows if row["Agent"] == agent]
                    total_prompt_tokens_used = sum(row["prompt_tokens used"] for row in agent_rows)
                    total_prompt_tokens_cost = sum(row["prompt_tokens cost"] for row in agent_rows)
                    total_completion_tokens_used = sum(row["completion_tokens used"] for row in agent_rows)
                    total_completion_tokens_cost = sum(row["completion_tokens cost"] for row in agent_rows)
                    total_tokens_used = sum(row["total_tokens used"] for row in agent_rows)
                    total_tokens_cost = sum(row["total_tokens cost"] for row in agent_rows)
                    total_duration = sum(float(row["Duration"][:-1]) for row in agent_rows) # [:-1] remove o caracter final, i.e. o 's'
                    average_duration = total_duration / len(agent_rows)
                    rows.append({
                        "File": file_name,
                        "Agent": agent,
                        "AI Model": "Total",
                        "prompt_tokens used": total_prompt_tokens_used,
                        "prompt_tokens cost": total_prompt_tokens_cost,
                        "completion_tokens used": total_completion_tokens_used,
                        "completion_tokens cost": total_completion_tokens_cost,
                        "total_tokens used": total_tokens_used,
                        "total_tokens cost": total_tokens_cost,
                        "Duration": f"{total_duration:.3f}s",
                        "Average Duration": f"{average_duration:.3f}s",
                    })

                # Calcular totais
                total_prompt_tokens_used = sum(row["prompt_tokens used"] for row in rows if row["AI Model"] != "Total")
                total_prompt_tokens_cost = sum(row["prompt_tokens cost"] for row in rows if row["AI Model"] != "Total")
                total_completion_tokens_used = sum(row["completion_tokens used"] for row in rows if row["AI Model"] != "Total")
                total_completion_tokens_cost = sum(row["completion_tokens cost"] for row in rows if row["AI Model"] != "Total")
                total_tokens_used = sum(row["total_tokens used"] for row in rows if row["AI Model"] != "Total")
                total_tokens_cost = sum(row["total_tokens cost"] for row in rows if row["AI Model"] != "Total")
                total_duration = sum(float(row["Duration"][:-1]) for row in rows if row["AI Model"] != "Total") # [:-1] remove o caracter final, i.e. o 's'
                rows.append({
                    "File": file_name,
                    "Agent": "-",
                    "AI Model": "Total",
                    "prompt_tokens used": total_prompt_tokens_used,
                    "prompt_tokens cost": total_prompt_tokens_cost,
                    "completion_tokens used": total_completion_tokens_used,
                    "completion_tokens cost": total_completion_tokens_cost,
                    "total_tokens used": total_tokens_used,
                    "total_tokens cost": total_tokens_cost,
                    "Duration": f"{total_duration:.3f}s",
                    "Average Duration": "-",
                })

                return rows
            except Exception as e:
                raise ValueError(f"Erro ao processar os dados: {e}")

        # Processar os dados
        rows = []
        sections = data.split("#####")[1:]  # Ignorar qualquer texto antes da primeira seção
        for section in sections:
            rows.extend(process_data_per_section(section))
        
        # Adicionar linha com totais de todos os ficheiros
        total_prompt_tokens_used = sum(row["prompt_tokens used"] for row in rows if row["AI Model"] != "Total")
        total_prompt_tokens_cost = sum(row["prompt_tokens cost"] for row in rows if row["AI Model"] != "Total")
        total_completion_tokens_used = sum(row["completion_tokens used"] for row in rows if row["AI Model"] != "Total")
        total_completion_tokens_cost = sum(row["completion_tokens cost"] for row in rows if row["AI Model"] != "Total")
        total_tokens_used = sum(row["total_tokens used"] for row in rows if row["AI Model"] != "Total")
        total_tokens_cost = sum(row["total_tokens cost"] for row in rows if row["AI Model"] != "Total")
        total_duration = sum(float(row["Duration"][:-1]) for row in rows if row["AI Model"] != "Total")
        rows.append({
            "File": "All Files",
            "Agent": "-",
            "AI Model": "Total",
            "prompt_tokens used": total_prompt_tokens_used,
            "prompt_tokens cost": total_prompt_tokens_cost,
            "completion_tokens used": total_completion_tokens_used,
            "completion_tokens cost": total_completion_tokens_cost,
            "total_tokens used": total_tokens_used,
            "total_tokens cost": total_tokens_cost,
            "Duration": f"{total_duration:.3f}s",
            "Average Duration": "-",
        })

        # Exportar para Excel
        try:
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            with pd.ExcelWriter(output_file_path, engine="openpyxl") as writer:
                # Escrever configurações
                # Prepare constants and pricing data for Excel
                constants_df = pd.DataFrame(list(constants.items()), columns=["Constants Descriptions", "Constants Values"])
                pricing_df = pd.DataFrame(
                    [(model, details["Pricing Input per 1M Tokens"], details["Pricing Output per 1M Tokens"]) for model, details in pricings.items()],
                    columns=["AI Models", "Pricing Input per 1M Tokens", "Pricing Output per 1M Tokens"],
                )
                
                # Determine the maximum length for alignment
                max_length = max(len(constants_df), len(pricing_df))
                
                # Extend dataframes to the same length
                constants_df = constants_df.reindex(range(max_length)).fillna("")
                pricing_df = pricing_df.reindex(range(max_length)).fillna("")
                
                # Combine constants and pricing data
                combined_df = pd.concat([constants_df, pd.DataFrame({"": [""] * max_length}), pricing_df], axis=1)
                
                # Write combined data to Excel
                combined_df.to_excel(writer, index=False, startrow=1, startcol=1)
                
                # Write main data to Excel
                pd.DataFrame(rows).to_excel(writer, index=False, startrow=max_length + 2 + 1, startcol=1) # +2 for the first and last empty rows and +1 for the header row
        except Exception as e:
            raise IOError(f"Erro ao exportar os dados para Excel: {e}")


    @staticmethod
    def __str__() -> str:
        return f"""
#################################### AI Analytics ####################################

{str(AiAnalytics.ai_files_analytics)}
######################################################################################
"""