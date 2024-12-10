import os
from unittest.mock import MagicMock
import openai
import logging
import time
import utility


# Mock the OpenAI API client
def mock_prompt_openai(text, m13id):
    # Simulate the API response you expect
    mock_response = """
    ```json
{
    "name_result": "Tian",
    "name_reasoning": "Nama kontak telah dinyatakan sebagai 'Tian' dalam percakapan.",
    "name_confidence": "100",
    "occupation_result": "Ibu Rumah Tangga",
    "occupation_reasoning": "Kontak membahas tentang anak-anak dan situasi di rumah tangga, yang menunjukkan dia berfokus pada kegiatan domestik.",
    "occupation_confidence": "85",
    "education_result": "SMA",
    "education_reasoning": "Dalam percakapan, kontak menyebutkan pendidikan terakhirnya adalah 'SMA'.",
    "education_confidence": "90",
    "age_result": "45",
    "age_reasoning": "Kontak menyebutkan bahwa dia berusia 45 tahun dalam percakapan.",
    "age_confidence": "95",
    "handphone_result": "082188375719",
    "handphone_reasoning": "Nomor tersebut disediakan oleh kontak sebagai nomor yang dapat dihubungi.",
    "handphone_confidence": "95",
    "marriage_result": "Menikah",
    "marriage_reasoning": "Kontak menyebutkan suami dan anak-anak, menunjukkan bahwa dia menikah.",
    "marriage_confidence": "90",
    "persona_initial_problem": "Sakit dan ingin sembuh.",
    "persona_initial_theme": "Kesehatan/Penyakit",
    "persona_pressing_problem": "Menghadapi masalah mental dan masalah keluarga.",
    "persona_pressing_theme": "Hubungan/Keluarga",
    "gender_result": "Perempuan",
    "gender_reasoning": "Konteks percakapan menunjukkan bahwa kontak adalah seorang ibu dan merujuk kepada suaminya.",
    "gender_confidence": "95",
    "address_province_result": "Sulawesi Selatan",
    "address_province_reasoning": "Kontak menyebutkan tinggal di Makassar, yang terletak di Sulawesi Selatan.",
    "address_province_confidence": "90",
    "address_city_result": "Makassar",
    "address_city_reasoning": "Kontak menyebutkan langsung 'Makassar' sebagai lokasi tinggal.",
    "address_city_confidence": "90",
    "address_kecamatan_result": "Biringkanaya",
    "address_kecamatan_reasoning": "Kontak menyebutkan kecamatan tempat tinggalnya sebagai 'Biringkanaya'.",
    "address_kecamatan_confidence": "90",
    "address_detail_result": "",
    "address_detail_reasoning": "Tidak ada detail tambahan yang diberikan dalam percakapan.",
    "address_detail_confidence": "70",
    "suku_result": "",
    "suku_reasoning": "Tidak ada referensi atau penyebutan suku dalam percakapan.",
    "suku_confidence": "100",
    "status_hp_result": "WA",
    "status_hp_reasoning": "Kontak memberikan nomor telpon untuk dihubungi via pesan, menunjukkan penggunaan WhatsApp.",
    "status_hp_confidence": "90",
    "attitude_result": "Open",
    "attitude_reasoning": "Kontak menunjukkan keterbukaan untuk berdiskusi tentang isu-isu spiritual dan kesehatan, serta ingin tahu lebih banyak.",
    "attitude_confidence": "80",
    "comments": "COD mengungkapkan masalah kesehatan dan ingin sembuh, serta membahas tantangan mental yang dihadapinya. Ia menunjukkan minat untuk mengenal lebih dalam tentang spiritualitas.",
    "comments_idn": "COD mengungkapkan masalah kesehatan dan ingin sembuh, serta membahas tantangan mental yang dihadapinya. Ia menunjukkan minat untuk mengenal lebih dalam tentang spiritualitas.",
    "recommendation": "Ajak COD untuk diskusi lebih lanjut tentang Isa Al-Masih, berikan perhatian pada masalah yang dihadapinya, dan tunjukkan empati.",
    "extra_info": "COD merasa nyaman berkomunikasi melalui pesan, dan memperlihatkan keinginan untuk membuka komunikasi lebih lanjut."
}
```

    """

    # Log the mock output for debugging purposes
    logging.debug(f"Mock response for conversation ID {m13id}: {mock_response}")

    # Return the mock response
    return mock_response


# Replacing the actual OpenAI API method with the mock
openai.OpenAI = MagicMock()
openai.OpenAI.chat.completions.create = mock_prompt_openai

# Test the API mock integration in the program
if __name__ == "__main__":
    # Simulate an input conversation text and m13id
    conversation_text = (
        "This is a mock conversation where we talk about career and personal issues."
    )
    m13id = "A 1234"

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Test the mocked prompt_openai function
    response = mock_prompt_openai(conversation_text, m13id)
    print(f"response type: {type(response)}")

    # Testing utility functions
    response = utility.clean_json(input_string=response)
    print(f"After clean up: \n{response}")

    contact = utility.parse_json_to_contact(json_data=response)
    utility.contacts_to_excel(contacts=[contact], excel_file_name="mock_test.xlsx")
