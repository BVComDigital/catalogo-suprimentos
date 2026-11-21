from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from .forms import CadastroUsuarioForm, EditarUsuarioForm

Usuario = get_user_model()


class TestePermissoesUsuarios(TestCase):

   def setUp(self): # é executado antes de cada teste da classe
      self.usuario = Usuario.objects.create_user(
         username='funcionario_teste',
         password='Teste@2026'
      )
      #Criamos o grupo Administrador local no banco temporário
      self.grupo_admin_local = Group.objects.create(
         name='Administrador local'
      )
      #Cria o grupo Funcionario
      self.grupo_funcionario = Group.objects.create(
         name='Funcionario'
      )
      #Localizamos a permissão gerenciar_usuarios
      self.permissao = Permission.objects.get(
         codename='gerenciar_usuarios'
      )
      #Associamos essa permissão ao grupo
      self.grupo_admin_local.permissions.add(self.permissao)

      #criar o usuário que representará o Administrador local
      self.admin_local = Usuario.objects.create_user(
         username='admin_local_teste',
         password='Teste@2026'
      )
      self.admin_local.groups.add(self.grupo_admin_local)

      self.outro_admin_local = Usuario.objects.create_user(
         username='outro_admin_teste',
         password='Teste@2026'
      )

      self.outro_admin_local.groups.add(self.grupo_admin_local)

      self.superusuario = Usuario.objects.create_superuser(
         username='superusuario_teste',
         email='super@teste.com',
         password='Teste@2026'
      )

      self.gerente = Usuario.objects.create_user(
         username='gerente_edicao',
         password='Teste@2026'
      )

      self.gerente.groups.add(
         Group.objects.create(name='Gerente')
      )

      self.funcionario = Usuario.objects.create_user(
         username='usuario_sem_grupo',
         password='Teste@2026'
      )

      # self.gerente.is_active = False
      # self.gerente.save()
      
      return super().setUp()

   

   def test_funcionario_nao_pode_listar_usuarios(self):
      # autentica o usuário de teste sem precisar preencher o formulário de login
      self.client.force_login(self.usuario) 
      # simula uma requisição GET à lista de usuários
      resposta = self.client.get('/usuarios/lista/')
      # verifica se a resposta HTTP foi 403 (acesso proibido).
      self.assertEqual(resposta.status_code, 403)

   def test_admin_local_pode_listar_usuarios(self):
      self.client.force_login(self.admin_local)
      resposta = self.client.get('/usuarios/lista/')
      self.assertEqual(resposta.status_code, 200)

   def test_admin_local_nao_pode_editar_outro_admin_local(self):
      self.client.force_login(self.admin_local)

      resposta = self.client.get(
         f'/usuarios/editar/{self.outro_admin_local.pk}/'
      )
      #Resposta esperada, página não encontrada, pois a view não permite o acesso  
      self.assertEqual(resposta.status_code, 404)

   def test_admin_local_nao_pode_editar_superusuario(self):
      self.client.force_login(self.admin_local)

      resposta = self.client.get(
         f'/usuarios/editar/{self.superusuario.pk}/'
      )

      self.assertEqual(resposta.status_code, 404)

   def test_cadastro_usuario_com_grupo_gerente(self):
      #Criamos o grupo Gerente no banco de testes
      grupo = Group.objects.get(name='Gerente')

      dados = {
         'username': 'gerente_teste',
         'password1': 'Teste@2026Senha',
         'password2': 'Teste@2026Senha',
         'grupo': grupo.pk
      }
      form = CadastroUsuarioForm(data=dados)

      self.assertTrue(form.is_valid())

   def test_cadastro_nao_aceita_grupo_admin_local(self):
      dados = {
         'username': 'tentativa_admin',
         'password1': 'Teste@2026Senha',
         'password2': 'Teste@2026Senha',
         'grupo': self.grupo_admin_local.pk
      }

      form = CadastroUsuarioForm(data=dados)

      self.assertFalse(form.is_valid())
      self.assertIn('grupo', form.errors)

   def test_editar_usuario_altera_grupo(self):
      grupo_funcionario = self.grupo_funcionario

      dados = {
         'username': self.gerente.username,
         'first_name': '',
         'last_name': '',
         'email': '',
         'grupo': grupo_funcionario.pk,
         'ativo': 'on'
      }

      form = EditarUsuarioForm(
         data=dados,
         instance=self.gerente
      )

      self.assertTrue(form.is_valid())

      form.save()

      self.assertEqual(
         list(self.gerente.groups.values_list('name', flat=True)),
         ['Funcionario']
      )

   def test_editar_usuario_desativa_conta(self):
      dados = {
         'username': self.gerente.username,
         'first_name': '',
         'last_name': '',
         'email': '',
         'grupo': self.gerente.groups.get().pk,
         'ativo': '' # recebe ativo desmarcado 
      }

      form = EditarUsuarioForm(
         data=dados,
         instance=self.gerente
      )

      self.assertTrue(form.is_valid())

      form.save()

      self.gerente.refresh_from_db() # atualiza o objeto com os dados do banco

      self.assertFalse(self.gerente.is_active)

   def test_editar_usuario_reativa_conta(self):
      dados = {
         'username': self.gerente.username,
         'first_name': '',
         'last_name': '',
         'email': '',
         'grupo': self.gerente.groups.get().pk,
         'ativo': 'on'
      }

      form = EditarUsuarioForm(
         data=dados,
         instance=self.gerente
      )

      self.assertTrue(form.is_valid())

      form.save()

      self.gerente.refresh_from_db()

      self.assertTrue(self.gerente.is_active)

   def test_admin_local_acessa_cadastro_usuario(self):
      self.client.force_login(self.admin_local)

      resposta = self.client.get('/usuarios/novo/')

      self.assertEqual(resposta.status_code, 200)

   def test_funcionario_nao_acessa_cadastro_usuario(self):
      self.client.force_login(self.usuario)

      resposta = self.client.get('/usuarios/novo/')

      self.assertEqual(resposta.status_code, 403)

   def test_admin_local_cadastra_gerente(self):
      grupo = Group.objects.get(name='Gerente')

      dados = {
         'username': 'novo_gerente',
         'password1': 'Teste@2026Senha',
         'password2': 'Teste@2026Senha',
         'grupo': grupo.pk
      }

      self.client.force_login(self.admin_local)

      resposta = self.client.post('/usuarios/novo/', dados)

      self.assertEqual(resposta.status_code, 302)

      novo_usuario = Usuario.objects.get(username='novo_gerente')

      self.assertTrue(
         novo_usuario.groups.filter(name='Gerente').exists()
      )

   def test_admin_local_acessa_edicao_gerente(self):
      self.client.force_login(self.admin_local)

      resposta = self.client.get(
         f'/usuarios/editar/{self.gerente.pk}/'
      )

      self.assertEqual(resposta.status_code, 200)

   def test_funcionario_nao_acessa_edicao_gerente(self):
      self.client.force_login(self.usuario)

      resposta = self.client.get(
         f'/usuarios/editar/{self.gerente.pk}/'
      )

      self.assertEqual(resposta.status_code, 403)

   def test_admin_local_edita_perfil_gerente(self):
      grupo = self.grupo_funcionario
      dados = {
         'username': self.gerente.username,
         'first_name': 'Joao',
         'last_name': 'Silva',
         'email': 'joao@teste.com',
         'grupo': grupo.pk,
         'ativo': 'on'
      }

      self.client.force_login(self.admin_local)

      resposta = self.client.post(
         f'/usuarios/editar/{self.gerente.pk}/',
         dados
      )

      self.assertEqual(resposta.status_code, 302)

      self.gerente.refresh_from_db()

      self.assertTrue(
         self.gerente.groups.filter(name='Funcionario').exists()
      )

      self.assertEqual(self.gerente.first_name, 'Joao')


   def test_usuario_anonimo_nao_pode_listar_usuarios(self):
      resposta = self.client.get('/usuarios/lista/')

      self.assertEqual(resposta.status_code, 302)

   def test_usuario_anonimo_nao_pode_acessar_cadastro(self):
      resposta = self.client.get('/usuarios/novo/')

      self.assertEqual(resposta.status_code, 302)

   def test_usuario_anonimo_nao_pode_editar_usuario(self):
      resposta = self.client.get(
         f'/usuarios/editar/{self.gerente.pk}/'
      )

      self.assertEqual(resposta.status_code, 302)

   def test_funcionario_nao_pode_editar_usuario_get(self):
      self.client.force_login(self.usuario)

      resposta = self.client.get(
         f'/usuarios/editar/{self.gerente.pk}/'
      )

      self.assertEqual(resposta.status_code, 403)

   def test_funcionario_nao_pode_cadastrar_usuario(self):
      self.client.force_login(self.usuario)

      resposta = self.client.post('/usuarios/novo/', {
         'username': 'usuario_bloqueado',
         'password1': 'Teste@2026',
         'password2': 'Teste@2026',
         'grupo': self.grupo_funcionario.pk,
      })

      self.assertEqual(resposta.status_code, 403)

      self.assertFalse(
         Usuario.objects.filter(
               username='usuario_bloqueado'
         ).exists()
      )

   def test_funcionario_nao_pode_editar_usuario(self):
      self.client.force_login(self.usuario)

      resposta = self.client.post(
         f'/usuarios/editar/{self.gerente.pk}/',
         {
               'username': self.gerente.username,
               'first_name': 'Alteracao indevida',
               'last_name': '',
               'email': '',
               'grupo': self.grupo_funcionario.pk,
               'ativo': 'on',
         }
      )

      self.assertEqual(resposta.status_code, 403)

      self.gerente.refresh_from_db()

      self.assertNotEqual(
         self.gerente.first_name,
         'Alteracao indevida'
      )

   def test_gerente_nao_pode_cadastrar_usuario(self):
      self.client.force_login(self.gerente)

      resposta = self.client.get('/usuarios/novo/')

      self.assertEqual(resposta.status_code, 403)

   def test_gerente_nao_pode_editar_usuario(self):
      self.client.force_login(self.gerente)

      resposta = self.client.get(
         f'/usuarios/editar/{self.outro_admin_local.pk}/'
      )

      self.assertEqual(resposta.status_code, 403)

      
   def test_gerente_nao_pode_cadastrar_usuario_por_post(self):
      self.client.force_login(self.gerente)

      resposta = self.client.post('/usuarios/novo/', {
         'username': 'gerente_bloqueado',
         'password1': 'Teste@2026',
         'password2': 'Teste@2026',
         'grupo': self.grupo_funcionario.pk,
      })

      self.assertEqual(resposta.status_code, 403)

      self.assertFalse(
         Usuario.objects.filter(
               username='gerente_bloqueado'
         ).exists()
      )


   def test_gerente_nao_pode_editar_usuario_por_post(self):
      self.client.force_login(self.gerente)

      resposta = self.client.post(
         f'/usuarios/editar/{self.outro_admin_local.pk}/',
         {
               'username': self.outro_admin_local.username,
               'first_name': 'Alteracao indevida',
               'last_name': '',
               'email': '',
               'grupo': self.grupo_funcionario.pk,
               'ativo': 'on',
         }
      )

      self.assertEqual(resposta.status_code, 403)

      self.outro_admin_local.refresh_from_db()

      self.assertNotEqual(
         self.outro_admin_local.first_name,
         'Alteracao indevida'
      )

   def test_admin_local_nao_pode_cadastrar_outro_admin_local(self):
      self.client.force_login(self.admin_local)

      resposta = self.client.post('/usuarios/novo/', {
         'username': 'admin_local_invasor',
         'password1': 'Teste@2026',
         'password2': 'Teste@2026',
         'grupo': self.grupo_admin_local.pk,
      })

      self.assertEqual(resposta.status_code, 200)

      self.assertFalse(
         Usuario.objects.filter(
               username='admin_local_invasor'
         ).exists()
      )
   
   def test_admin_local_nao_pode_alterar_proprio_grupo_para_admin_local(self):
      self.client.force_login(self.admin_local)

      resposta = self.client.post(
         f'/usuarios/editar/{self.admin_local.pk}/',
         {
               'username': self.admin_local.username,
               'first_name': '',
               'last_name': '',
               'email': '',
               'grupo': self.grupo_admin_local.pk,
               'ativo': 'on',
         }
      )

      self.assertEqual(resposta.status_code, 404)


   def test_admin_local_nao_pode_promover_usuario_para_admin_local(self):
      self.client.force_login(self.admin_local)

      resposta = self.client.post(
         f'/usuarios/editar/{self.gerente.pk}/',
         {
               'username': self.gerente.username,
               'first_name': '',
               'last_name': '',
               'email': '',
               'grupo': self.grupo_admin_local.pk,
               'ativo': 'on',
         }
      )

      self.assertEqual(resposta.status_code, 200)

      self.gerente.refresh_from_db()

      self.assertFalse(
         self.gerente.groups.filter(
               name='Administrador local'
         ).exists()
      )

   def test_superusuario_acessa_cadastro_usuario(self):
      self.client.force_login(self.superusuario)

      resposta = self.client.get('/usuarios/novo/')

      self.assertEqual(resposta.status_code, 200)   

   def test_gerente_nao_pode_editar_admin_local(self):
      self.client.force_login(self.gerente)

      resposta = self.client.get(
         f'/usuarios/editar/{self.admin_local.pk}/'
      )

      self.assertEqual(resposta.status_code, 403)

   def test_funcionario_nao_pode_editar_admin_local(self):
      self.client.force_login(self.usuario)

      resposta = self.client.get(
         f'/usuarios/editar/{self.admin_local.pk}/'
      )

      self.assertEqual(resposta.status_code, 403)

   def test_admin_local_nao_pode_editar_superusuario_por_post(self):
      self.client.force_login(self.admin_local)

      resposta = self.client.post(
         f'/usuarios/editar/{self.superusuario.pk}/',
         {
               'username': self.superusuario.username,
               'first_name': 'Alteracao indevida',
               'last_name': '',
               'email': 'teste@teste.com',
               'grupo': self.grupo_funcionario.pk,
               'ativo': 'on',
         }
      )

      self.assertEqual(resposta.status_code, 404)

      self.superusuario.refresh_from_db()

      self.assertNotEqual(
         self.superusuario.first_name,
         'Alteracao indevida'
      )

   def test_funcionario_nao_pode_editar_superusuario_por_post(self):
      self.client.force_login(self.usuario)

      resposta = self.client.post(
         f'/usuarios/editar/{self.superusuario.pk}/',
         {
               'username': self.superusuario.username,
               'first_name': 'Alteracao indevida',
               'last_name': '',
               'email': 'teste@teste.com',
               'grupo': self.grupo_funcionario.pk,
               'ativo': 'on',
         }
      )

      self.assertEqual(resposta.status_code, 403)

      self.superusuario.refresh_from_db()

      self.assertNotEqual(
         self.superusuario.first_name,
         'Alteracao indevida'
      )

   def test_gerente_nao_pode_editar_superusuario_por_post(self):
      self.client.force_login(self.gerente)

      resposta = self.client.post(
         f'/usuarios/editar/{self.superusuario.pk}/',
         {
               'username': self.superusuario.username,
               'first_name': 'Alteracao indevida',
               'last_name': '',
               'email': 'teste@teste.com',
               'grupo': self.grupo_funcionario.pk,
               'ativo': 'on',
         }
      )

      self.assertEqual(resposta.status_code, 403)

      self.superusuario.refresh_from_db()

      self.assertNotEqual(
         self.superusuario.first_name,
         'Alteracao indevida'
      )

   def test_funcionario_nao_pode_acessar_cadastro_por_get(self):
      self.client.force_login(self.usuario)

      resposta = self.client.get('/usuarios/novo/')

      self.assertEqual(resposta.status_code, 403)


   def test_funcionario_nao_pode_listar_usuarios_por_post(self):
      self.client.force_login(self.usuario)

      resposta = self.client.post('/usuarios/lista/')

      self.assertEqual(resposta.status_code, 403)

   def test_gerente_nao_pode_listar_usuarios_por_post(self):
      self.client.force_login(self.gerente)

      resposta = self.client.post('/usuarios/lista/')

      self.assertEqual(resposta.status_code, 403)

   def test_admin_local_nao_pode_editar_usuario_sem_grupo_permitido(self):
      self.client.force_login(self.admin_local)

      resposta = self.client.get(
         f'/usuarios/editar/{self.funcionario.pk}/'
      )

      self.assertEqual(resposta.status_code, 404)