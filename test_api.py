import unittest
from unittest.mock import patch

from app import create_app


class ApiRouteTests(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_health_route(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "API on"})

    @patch("api.quiz.query_all")
    def test_quiz_list_route_omits_answer(self, query_all):
        query_all.return_value = [
            {
                "id": 1,
                "tema": "sintaxe",
                "nivel": "facil",
                "pergunta": "Pergunta?",
                "alt_a": "A",
                "alt_b": "B",
                "alt_c": "C",
                "alt_d": "D",
                "resposta": "B",
            }
        ]

        response = self.client.get(
            "/quiz/?tema=sintaxe&nivel=facil&limite=1"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            [
                {
                    "id": 1,
                    "tema": "sintaxe",
                    "nivel": "facil",
                    "pergunta": "Pergunta?",
                    "alternativas": {"A": "A", "B": "B", "C": "C", "D": "D"},
                }
            ],
        )
        self.assertNotIn("resposta", response.get_json()[0])
        self.assertIn("tema = %s", query_all.call_args.args[0])
        self.assertIn("nivel = %s", query_all.call_args.args[0])
        self.assertEqual(query_all.call_args.args[1], ["sintaxe", "facil", 1])

    @patch("api.quiz.pontuar", return_value=20)
    @patch("api.quiz.query_one")
    def test_quiz_answer_route(self, query_one, pontuar):
        query_one.return_value = {
            "resposta": "B",
            "nivel": "medio",
            "explicacao": "Explicação.",
        }

        response = self.client.post(
            "/quiz/1/responder",
            json={"apelido": "ana", "resposta": "b"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "correta": True,
                "resposta_certa": "B",
                "explicacao": "Explicação.",
                "pontos_totais": 20,
            },
        )
        pontuar.assert_called_once_with("ana", True, 20)

    @patch("api.flashcards.query_all")
    def test_flashcards_list_route(self, query_all):
        query_all.return_value = [
            {
                "id": 1,
                "tema": "morfologia",
                "frente": "O que é radical?",
                "verso": "Parte da palavra.",
            }
        ]

        response = self.client.get("/flashcards/?tema=morfologia&limite=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["frente"], "O que é radical?")
        self.assertEqual(response.get_json()[0]["verso"], "Parte da palavra.")
        self.assertEqual(query_all.call_args.args[1], ["morfologia", 1])

    @patch("api.flashcards.pontuar", return_value=5)
    @patch("api.flashcards.query_one", return_value={"?column?": 1})
    def test_flashcard_review_route(self, query_one, pontuar):
        response = self.client.post(
            "/flashcards/1/revisar",
            json={"apelido": "ana", "sabia": True},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(), {"sabia": True, "pontos_totais": 5}
        )
        query_one.assert_called_once()
        pontuar.assert_called_once_with("ana", True, 5)

    @patch("api.lacunas.query_all")
    def test_gaps_list_route_omits_answer(self, query_all):
        query_all.return_value = [
            {
                "id": 1,
                "tema": "sintaxe",
                "frase": "Ele chegou ___ casa cedo.",
                "opcoes": ["em", "a", "na"],
            }
        ]

        response = self.client.get("/lacunas/?tema=sintaxe&limite=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            [
                {
                    "id": 1,
                    "tema": "sintaxe",
                    "frase": "Ele chegou ___ casa cedo.",
                    "opcoes": ["em", "a", "na"],
                }
            ],
        )
        self.assertNotIn("resposta", response.get_json()[0])

    @patch("api.lacunas.pontuar", return_value=15)
    @patch("api.lacunas.query_one")
    def test_gap_answer_route(self, query_one, pontuar):
        query_one.return_value = {
            "resposta": "a",
            "explicacao": "Explicação.",
        }

        response = self.client.post(
            "/lacunas/1/responder",
            json={"apelido": "ana", "resposta": "A"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "correta": True,
                "resposta_certa": "a",
                "explicacao": "Explicação.",
                "pontos_totais": 15,
            },
        )
        pontuar.assert_called_once_with("ana", True, 15)

    @patch("api.jogadores.query_all")
    def test_ranking_route(self, query_all):
        query_all.return_value = [{"apelido": "ana", "pontos": 120}]

        response = self.client.get("/ranking")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(), [{"apelido": "ana", "pontos": 120}]
        )

    @patch("api.jogadores.query_one")
    def test_existing_player_profile_route(self, query_one):
        query_one.return_value = {
            "apelido": "ana",
            "pontos": 120,
            "acertos": 8,
            "erros": 3,
        }

        response = self.client.get("/jogadores/ana")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), query_one.return_value)

    @patch("api.jogadores.query_one", return_value=None)
    def test_missing_player_profile_route(self, query_one):
        response = self.client.get("/jogadores/ana")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"apelido": "ana", "pontos": 0, "acertos": 0, "erros": 0},
        )
        query_one.assert_called_once()

    @patch("api.quiz.query_one")
    def test_quiz_answer_rejects_invalid_body(self, query_one):
        response = self.client.post(
            "/quiz/1/responder",
            json={"apelido": "ana", "resposta": "E"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("erro", response.get_json())
        query_one.assert_not_called()

    @patch("api.flashcards.query_one")
    def test_flashcard_review_rejects_non_boolean(self, query_one):
        response = self.client.post(
            "/flashcards/1/revisar",
            json={"apelido": "ana", "sabia": "true"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("erro", response.get_json())
        query_one.assert_not_called()

    @patch("api.lacunas.query_one", return_value=None)
    def test_gap_answer_returns_not_found(self, query_one):
        response = self.client.post(
            "/lacunas/999/responder",
            json={"apelido": "ana", "resposta": "a"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn("erro", response.get_json())
        query_one.assert_called_once()


if __name__ == "__main__":
    unittest.main()
