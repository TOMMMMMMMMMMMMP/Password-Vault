from controller.vault_controller import VaultController
from view.login_view import LoginView
from view.vault_view import VaultView


def main():
    controller = VaultController()

    login = LoginView(controller)
    login.mainloop()

    if login.result:
        vault = VaultView(controller)
        vault.mainloop()


if __name__ == "__main__":
    main()
