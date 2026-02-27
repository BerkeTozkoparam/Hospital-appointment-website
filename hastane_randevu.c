#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <locale.h>
#include <ncurses.h>

/* ---- Renk Sabitleri ---- */
#define C_BASLIK 1
#define C_SECILI 2
#define C_NORMAL 3
#define C_BASARI 4
#define C_HATA   5
#define C_BILGI  6

/* ---- Dosya Adlari ---- */
#define HASTA_DOSYA   "hastalar.dat"
#define DOKTOR_DOSYA  "doktorlar.dat"
#define RANDEVU_DOSYA "randevular.dat"

/* ===================== YAPILAR ===================== */

typedef struct {
    int id;
    char ad[50];
    char soyad[50];
    int yas;
    char telefon[15];
    char tcno[12];
} Hasta;

typedef struct {
    int id;
    char ad[50];
    char soyad[50];
    char uzmanlik[50];
    char telefon[15];
} Doktor;

typedef struct {
    int id;
    int hasta_id;
    int doktor_id;
    char tarih[11];
    char saat[6];
    char durum[10];
} Randevu;

/* ===================== DOSYA YARDIMCI ===================== */

int hasta_sayisi_al() {
    FILE *f = fopen(HASTA_DOSYA, "rb");
    if (!f) return 0;
    fseek(f, 0, SEEK_END);
    int s = ftell(f) / sizeof(Hasta);
    fclose(f);
    return s;
}

int doktor_sayisi_al() {
    FILE *f = fopen(DOKTOR_DOSYA, "rb");
    if (!f) return 0;
    fseek(f, 0, SEEK_END);
    int s = ftell(f) / sizeof(Doktor);
    fclose(f);
    return s;
}

int randevu_sayisi_al() {
    FILE *f = fopen(RANDEVU_DOSYA, "rb");
    if (!f) return 0;
    fseek(f, 0, SEEK_END);
    int s = ftell(f) / sizeof(Randevu);
    fclose(f);
    return s;
}

/* ===================== NCURSES YARDIMCI ===================== */

void ncurses_baslat() {
    setlocale(LC_ALL, "");
    initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    curs_set(0);
    if (has_colors()) {
        start_color();
        use_default_colors();
        init_pair(C_BASLIK, COLOR_CYAN,   -1);
        init_pair(C_SECILI, COLOR_BLACK,  COLOR_CYAN);
        init_pair(C_NORMAL, COLOR_WHITE,  -1);
        init_pair(C_BASARI, COLOR_GREEN,  -1);
        init_pair(C_HATA,   COLOR_RED,    -1);
        init_pair(C_BILGI,  COLOR_YELLOW, -1);
    }
}

void baslik_ciz(const char *baslik) {
    int rows, cols;
    getmaxyx(stdscr, rows, cols);
    (void)rows;
    box(stdscr, 0, 0);
    int len = (int)strlen(baslik) + 4;
    int x = (cols - len) / 2;
    if (x < 1) x = 1;
    attron(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvprintw(1, x, "[ %s ]", baslik);
    attroff(A_BOLD | COLOR_PAIR(C_BASLIK));
    attron(COLOR_PAIR(C_BASLIK));
    mvhline(2, 1, ACS_HLINE, cols - 2);
    attroff(COLOR_PAIR(C_BASLIK));
}

void bilgi_satiri(const char *metin) {
    int rows, cols;
    getmaxyx(stdscr, rows, cols);
    attron(COLOR_PAIR(C_BASLIK));
    mvhline(rows - 2, 1, ACS_HLINE, cols - 2);
    attroff(COLOR_PAIR(C_BASLIK));
    attron(A_DIM | COLOR_PAIR(C_BILGI));
    mvprintw(rows - 2, 2, " %s ", metin);
    attroff(A_DIM | COLOR_PAIR(C_BILGI));
}

void mesaj_popup(const char *mesaj, int renk) {
    int rows, cols;
    getmaxyx(stdscr, rows, cols);
    int w = (int)strlen(mesaj) + 6;
    if (w < 26) w = 26;
    int h = 5;
    int y = (rows - h) / 2;
    int x = (cols - w) / 2;
    WINDOW *win = newwin(h, w, y, x);
    box(win, 0, 0);
    wattron(win, A_BOLD | COLOR_PAIR(renk));
    mvwprintw(win, 1, (w - (int)strlen(mesaj)) / 2, "%s", mesaj);
    wattroff(win, A_BOLD | COLOR_PAIR(renk));
    wattron(win, A_DIM | COLOR_PAIR(C_BILGI));
    mvwprintw(win, h - 1, (w - 18) / 2, "[ Enter: Devam ]");
    wattroff(win, A_DIM | COLOR_PAIR(C_BILGI));
    wrefresh(win);
    wgetch(win);
    delwin(win);
    touchwin(stdscr);
    refresh();
}

void input_str(int y, int x, char *buf, int maxlen) {
    int rows_dummy, cols;
    getmaxyx(stdscr, rows_dummy, cols);
    (void)rows_dummy;
    int dlen = maxlen;
    if (x + dlen > cols - 2) dlen = cols - 2 - x;
    if (dlen <= 0) dlen = 10;
    echo();
    curs_set(1);
    attron(A_UNDERLINE | COLOR_PAIR(C_NORMAL));
    for (int i = 0; i < dlen; i++) mvaddch(y, x + i, ' ');
    attroff(A_UNDERLINE | COLOR_PAIR(C_NORMAL));
    move(y, x);
    refresh();
    getnstr(buf, maxlen - 1);
    noecho();
    curs_set(0);
}

void input_int(int y, int x, int *val) {
    char buf[16] = {0};
    input_str(y, x, buf, 16);
    *val = atoi(buf);
}

/* ===================== INTERAKTIF MENU ===================== */
/* Secilen secenegin 0 tabanli indexini dondurur. ESC icin -1. */

int menu_goster(const char *baslik, const char *opts[], int n) {
    int secim = 0;
    while (1) {
        clear();
        int rows, cols;
        getmaxyx(stdscr, rows, cols);
        baslik_ciz(baslik);
        bilgi_satiri("[Yukari/Asagi] Gezin   [Enter] Sec   [ESC] Cikis/Geri");

        int max_len = 0;
        for (int i = 0; i < n; i++) {
            int l = (int)strlen(opts[i]);
            if (l > max_len) max_len = l;
        }
        int opt_w   = max_len + 10;
        int opt_x   = (cols - opt_w) / 2;
        int total_h = n * 2 - 1;
        int start_y = (rows - total_h) / 2;
        if (start_y < 4) start_y = 4;

        for (int i = 0; i < n; i++) {
            int oy = start_y + i * 2;
            if (i == secim) {
                attron(A_BOLD | COLOR_PAIR(C_SECILI));
                mvprintw(oy, opt_x, "  >> %-*s  ", max_len, opts[i]);
                attroff(A_BOLD | COLOR_PAIR(C_SECILI));
            } else {
                attron(COLOR_PAIR(C_NORMAL));
                mvprintw(oy, opt_x, "     %-*s  ", max_len, opts[i]);
                attroff(COLOR_PAIR(C_NORMAL));
            }
        }
        refresh();

        int ch = getch();
        switch (ch) {
            case KEY_UP:    secim = (secim - 1 + n) % n; break;
            case KEY_DOWN:  secim = (secim + 1) % n;     break;
            case '\n':
            case '\r':
            case KEY_ENTER: return secim;
            case 27:        return -1;
        }
    }
}

/* ===================== HASTA FONKSIYONLARI ===================== */

void hasta_ekle() {
    clear();
    baslik_ciz("HASTA KAYDI");
    bilgi_satiri("[Enter] Her alani doldurup onaylayin");

    Hasta h = {0};
    h.id = hasta_sayisi_al() + 1;

    int y = 5, lx = 6, ix = 24;
    attron(COLOR_PAIR(C_BILGI) | A_BOLD);
    mvprintw(y,     lx, "Ad              :");
    mvprintw(y + 2, lx, "Soyad           :");
    mvprintw(y + 4, lx, "Yas             :");
    mvprintw(y + 6, lx, "Telefon         :");
    mvprintw(y + 8, lx, "TC No           :");
    attroff(COLOR_PAIR(C_BILGI) | A_BOLD);
    refresh();

    char buf[16];
    input_str(y,     ix, h.ad,      49);
    input_str(y + 2, ix, h.soyad,   49);
    input_str(y + 4, ix, buf,       10); h.yas = atoi(buf);
    input_str(y + 6, ix, h.telefon, 14);
    input_str(y + 8, ix, h.tcno,    11);

    FILE *f = fopen(HASTA_DOSYA, "ab");
    if (!f) { mesaj_popup("Dosya acilamadi!", C_HATA); return; }
    fwrite(&h, sizeof(Hasta), 1, f);
    fclose(f);

    char msg[64];
    snprintf(msg, sizeof(msg), "Hasta kaydedildi!  (ID: %d)", h.id);
    mesaj_popup(msg, C_BASARI);
}

void hasta_listele() {
    clear();
    int rows, cols;
    getmaxyx(stdscr, rows, cols);
    baslik_ciz("HASTA LISTESI");
    bilgi_satiri("[Herhangi bir tus] Geri");

    FILE *f = fopen(HASTA_DOSYA, "rb");
    if (!f) {
        attron(COLOR_PAIR(C_HATA));
        mvprintw(5, 4, "Kayitli hasta bulunamadi.");
        attroff(COLOR_PAIR(C_HATA));
        refresh(); getch(); return;
    }

    int y = 4;
    attron(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvprintw(y, 2, "%-4s  %-14s  %-14s  %-4s  %-13s  %-11s",
             "ID", "Ad", "Soyad", "Yas", "Telefon", "TC No");
    attroff(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvhline(y + 1, 2, ACS_HLINE, cols - 4);

    Hasta h;
    int row = y + 2, toplam = 0;
    while (fread(&h, sizeof(Hasta), 1, f) && row < rows - 3) {
        if (toplam % 2 == 0) attron(A_DIM);
        mvprintw(row, 2, "%-4d  %-14s  %-14s  %-4d  %-13s  %-11s",
                 h.id, h.ad, h.soyad, h.yas, h.telefon, h.tcno);
        if (toplam % 2 == 0) attroff(A_DIM);
        row++; toplam++;
    }
    fclose(f);

    attron(COLOR_PAIR(C_BILGI));
    mvprintw(rows - 3, 2, "Toplam: %d hasta", toplam);
    attroff(COLOR_PAIR(C_BILGI));
    refresh(); getch();
}

void hasta_ara() {
    clear();
    baslik_ciz("HASTA ARA");
    bilgi_satiri("[Enter] Ara");

    attron(COLOR_PAIR(C_BILGI) | A_BOLD);
    mvprintw(5, 6, "Aranacak ad veya soyad:");
    attroff(COLOR_PAIR(C_BILGI) | A_BOLD);
    refresh();

    char aranan[50] = {0};
    input_str(5, 30, aranan, 49);
    if (!aranan[0]) return;

    clear();
    int rows, cols;
    getmaxyx(stdscr, rows, cols);
    baslik_ciz("ARAMA SONUCLARI");
    bilgi_satiri("[Herhangi bir tus] Geri");

    FILE *f = fopen(HASTA_DOSYA, "rb");
    if (!f) { mesaj_popup("Hasta dosyasi bulunamadi.", C_HATA); return; }

    Hasta h;
    int y = 4, bulunan = 0;
    attron(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvprintw(y, 2, "%-4s  %-14s  %-14s  %-4s  %-13s", "ID","Ad","Soyad","Yas","Telefon");
    attroff(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvhline(y + 1, 2, ACS_HLINE, cols - 4);
    y += 2;

    while (fread(&h, sizeof(Hasta), 1, f) && y < rows - 3) {
        if (strstr(h.ad, aranan) || strstr(h.soyad, aranan)) {
            if (bulunan % 2 == 0) attron(A_DIM);
            mvprintw(y++, 2, "%-4d  %-14s  %-14s  %-4d  %-13s",
                     h.id, h.ad, h.soyad, h.yas, h.telefon);
            if (bulunan % 2 == 0) attroff(A_DIM);
            bulunan++;
        }
    }
    fclose(f);

    if (bulunan) {
        attron(COLOR_PAIR(C_BILGI));
        mvprintw(rows - 3, 2, "%d kayit bulundu.", bulunan);
        attroff(COLOR_PAIR(C_BILGI));
    } else {
        attron(COLOR_PAIR(C_HATA));
        mvprintw(y, 2, "Eslesen kayit bulunamadi.");
        attroff(COLOR_PAIR(C_HATA));
    }
    refresh(); getch();
}

void hasta_sil() {
    clear();
    baslik_ciz("HASTA SIL");
    bilgi_satiri("[Enter] Onayla");

    attron(COLOR_PAIR(C_HATA) | A_BOLD);
    mvprintw(5, 6, "Silinecek hasta ID:");
    attroff(COLOR_PAIR(C_HATA) | A_BOLD);
    refresh();

    int id = 0;
    input_int(5, 26, &id);

    FILE *f = fopen(HASTA_DOSYA, "rb");
    if (!f) { mesaj_popup("Dosya bulunamadi.", C_HATA); return; }
    FILE *tmp = fopen("tmp_hasta.dat", "wb");
    Hasta h; int silindi = 0;
    while (fread(&h, sizeof(Hasta), 1, f)) {
        if (h.id == id) { silindi = 1; continue; }
        fwrite(&h, sizeof(Hasta), 1, tmp);
    }
    fclose(f); fclose(tmp);
    remove(HASTA_DOSYA);
    rename("tmp_hasta.dat", HASTA_DOSYA);

    mesaj_popup(silindi ? "Hasta silindi." : "Hasta bulunamadi!",
                silindi ? C_BASARI : C_HATA);
}

/* ===================== DOKTOR FONKSIYONLARI ===================== */

void doktor_ekle() {
    clear();
    baslik_ciz("DOKTOR KAYDI");
    bilgi_satiri("[Enter] Her alani doldurup onaylayin");

    Doktor d = {0};
    d.id = doktor_sayisi_al() + 1;

    int y = 5, lx = 6, ix = 24;
    attron(COLOR_PAIR(C_BILGI) | A_BOLD);
    mvprintw(y,     lx, "Ad              :");
    mvprintw(y + 2, lx, "Soyad           :");
    mvprintw(y + 4, lx, "Uzmanlik        :");
    mvprintw(y + 6, lx, "Telefon         :");
    attroff(COLOR_PAIR(C_BILGI) | A_BOLD);
    refresh();

    input_str(y,     ix, d.ad,       49);
    input_str(y + 2, ix, d.soyad,    49);
    input_str(y + 4, ix, d.uzmanlik, 49);
    input_str(y + 6, ix, d.telefon,  14);

    FILE *f = fopen(DOKTOR_DOSYA, "ab");
    if (!f) { mesaj_popup("Dosya acilamadi!", C_HATA); return; }
    fwrite(&d, sizeof(Doktor), 1, f);
    fclose(f);

    char msg[64];
    snprintf(msg, sizeof(msg), "Doktor kaydedildi!  (ID: %d)", d.id);
    mesaj_popup(msg, C_BASARI);
}

void doktor_listele() {
    clear();
    int rows, cols;
    getmaxyx(stdscr, rows, cols);
    baslik_ciz("DOKTOR LISTESI");
    bilgi_satiri("[Herhangi bir tus] Geri");

    FILE *f = fopen(DOKTOR_DOSYA, "rb");
    if (!f) {
        attron(COLOR_PAIR(C_HATA));
        mvprintw(5, 4, "Kayitli doktor bulunamadi.");
        attroff(COLOR_PAIR(C_HATA));
        refresh(); getch(); return;
    }

    int y = 4;
    attron(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvprintw(y, 2, "%-4s  %-14s  %-14s  %-18s  %-13s",
             "ID", "Ad", "Soyad", "Uzmanlik", "Telefon");
    attroff(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvhline(y + 1, 2, ACS_HLINE, cols - 4);

    Doktor d;
    int row = y + 2, toplam = 0;
    while (fread(&d, sizeof(Doktor), 1, f) && row < rows - 3) {
        if (toplam % 2 == 0) attron(A_DIM);
        mvprintw(row, 2, "%-4d  %-14s  %-14s  %-18s  %-13s",
                 d.id, d.ad, d.soyad, d.uzmanlik, d.telefon);
        if (toplam % 2 == 0) attroff(A_DIM);
        row++; toplam++;
    }
    fclose(f);

    attron(COLOR_PAIR(C_BILGI));
    mvprintw(rows - 3, 2, "Toplam: %d doktor", toplam);
    attroff(COLOR_PAIR(C_BILGI));
    refresh(); getch();
}

void doktor_sil() {
    clear();
    baslik_ciz("DOKTOR SIL");
    bilgi_satiri("[Enter] Onayla");

    attron(COLOR_PAIR(C_HATA) | A_BOLD);
    mvprintw(5, 6, "Silinecek doktor ID:");
    attroff(COLOR_PAIR(C_HATA) | A_BOLD);
    refresh();

    int id = 0;
    input_int(5, 27, &id);

    FILE *f = fopen(DOKTOR_DOSYA, "rb");
    if (!f) { mesaj_popup("Dosya bulunamadi.", C_HATA); return; }
    FILE *tmp = fopen("tmp_doktor.dat", "wb");
    Doktor d; int silindi = 0;
    while (fread(&d, sizeof(Doktor), 1, f)) {
        if (d.id == id) { silindi = 1; continue; }
        fwrite(&d, sizeof(Doktor), 1, tmp);
    }
    fclose(f); fclose(tmp);
    remove(DOKTOR_DOSYA);
    rename("tmp_doktor.dat", DOKTOR_DOSYA);

    mesaj_popup(silindi ? "Doktor silindi." : "Doktor bulunamadi!",
                silindi ? C_BASARI : C_HATA);
}

/* ===================== RANDEVU FONKSIYONLARI ===================== */

void randevu_al() {
    clear();
    int rows, cols;
    getmaxyx(stdscr, rows, cols);
    baslik_ciz("RANDEVU AL");
    bilgi_satiri("[Enter] Her alani doldurup onaylayin");

    FILE *fh = fopen(HASTA_DOSYA, "rb");
    if (!fh) { mesaj_popup("Once hasta kaydedin!", C_HATA); return; }

    int y = 4;
    attron(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvprintw(y++, 2, "--- Hastalar ---");
    attroff(A_BOLD | COLOR_PAIR(C_BASLIK));
    Hasta h;
    while (fread(&h, sizeof(Hasta), 1, fh) && y < rows / 2)
        mvprintw(y++, 4, "[%d] %s %s", h.id, h.ad, h.soyad);
    fclose(fh);

    y++;
    FILE *fd = fopen(DOKTOR_DOSYA, "rb");
    if (!fd) { mesaj_popup("Once doktor kaydedin!", C_HATA); return; }

    attron(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvprintw(y++, 2, "--- Doktorlar ---");
    attroff(A_BOLD | COLOR_PAIR(C_BASLIK));
    Doktor d;
    while (fread(&d, sizeof(Doktor), 1, fd) && y < rows - 9)
        mvprintw(y++, 4, "[%d] Dr. %s %s  (%s)", d.id, d.ad, d.soyad, d.uzmanlik);
    fclose(fd);

    y++;
    Randevu r = {0};
    r.id = randevu_sayisi_al() + 1;
    strcpy(r.durum, "Aktif");

    int lx = 2, ix = 24;
    attron(COLOR_PAIR(C_BILGI) | A_BOLD);
    mvprintw(y,     lx, "Hasta ID           :");
    mvprintw(y + 2, lx, "Doktor ID          :");
    mvprintw(y + 4, lx, "Tarih (GG/AA/YYYY) :");
    mvprintw(y + 6, lx, "Saat  (HH:MM)      :");
    attroff(COLOR_PAIR(C_BILGI) | A_BOLD);
    refresh();

    input_int(y,     ix, &r.hasta_id);
    input_int(y + 2, ix, &r.doktor_id);
    input_str(y + 4, ix, r.tarih, 10);
    input_str(y + 6, ix, r.saat,   5);

    FILE *fr = fopen(RANDEVU_DOSYA, "ab");
    if (!fr) { mesaj_popup("Dosya acilamadi!", C_HATA); return; }
    fwrite(&r, sizeof(Randevu), 1, fr);
    fclose(fr);

    char msg[64];
    snprintf(msg, sizeof(msg), "Randevu alindi!  (ID: %d)", r.id);
    mesaj_popup(msg, C_BASARI);
}

void randevu_listele() {
    clear();
    int rows, cols;
    getmaxyx(stdscr, rows, cols);
    baslik_ciz("RANDEVU LISTESI");
    bilgi_satiri("[Herhangi bir tus] Geri");

    FILE *f = fopen(RANDEVU_DOSYA, "rb");
    if (!f) {
        attron(COLOR_PAIR(C_HATA));
        mvprintw(5, 4, "Kayitli randevu bulunamadi.");
        attroff(COLOR_PAIR(C_HATA));
        refresh(); getch(); return;
    }

    int y = 4;
    attron(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvprintw(y, 2, "%-4s  %-8s  %-9s  %-11s  %-6s  %-7s",
             "ID", "Hasta", "Doktor", "Tarih", "Saat", "Durum");
    attroff(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvhline(y + 1, 2, ACS_HLINE, cols - 4);

    Randevu r;
    int row = y + 2, toplam = 0;
    while (fread(&r, sizeof(Randevu), 1, f) && row < rows - 3) {
        int renk = (strcmp(r.durum, "Iptal") == 0) ? C_HATA : C_BASARI;
        attron(COLOR_PAIR(renk));
        mvprintw(row, 2, "%-4d  %-8d  %-9d  %-11s  %-6s  %-7s",
                 r.id, r.hasta_id, r.doktor_id, r.tarih, r.saat, r.durum);
        attroff(COLOR_PAIR(renk));
        row++; toplam++;
    }
    fclose(f);

    attron(COLOR_PAIR(C_BILGI));
    mvprintw(rows - 3, 2, "Toplam: %d randevu", toplam);
    attroff(COLOR_PAIR(C_BILGI));
    refresh(); getch();
}

void randevu_iptal() {
    clear();
    baslik_ciz("RANDEVU IPTAL");
    bilgi_satiri("[Enter] Onayla");

    attron(COLOR_PAIR(C_HATA) | A_BOLD);
    mvprintw(5, 6, "Iptal edilecek randevu ID:");
    attroff(COLOR_PAIR(C_HATA) | A_BOLD);
    refresh();

    int id = 0;
    input_int(5, 33, &id);

    FILE *f = fopen(RANDEVU_DOSYA, "r+b");
    if (!f) { mesaj_popup("Dosya bulunamadi.", C_HATA); return; }

    Randevu r; int bulundu = 0;
    while (fread(&r, sizeof(Randevu), 1, f)) {
        if (r.id == id) {
            strcpy(r.durum, "Iptal");
            fseek(f, -(long)sizeof(Randevu), SEEK_CUR);
            fwrite(&r, sizeof(Randevu), 1, f);
            bulundu = 1; break;
        }
    }
    fclose(f);

    mesaj_popup(bulundu ? "Randevu iptal edildi." : "Randevu bulunamadi!",
                bulundu ? C_BASARI : C_HATA);
}

void randevu_hasta_goruntule() {
    clear();
    baslik_ciz("HASTANIN RANDEVULARI");
    bilgi_satiri("[Enter] Ara");

    attron(COLOR_PAIR(C_BILGI) | A_BOLD);
    mvprintw(5, 6, "Hasta ID:");
    attroff(COLOR_PAIR(C_BILGI) | A_BOLD);
    refresh();

    int hasta_id = 0;
    input_int(5, 16, &hasta_id);

    clear();
    int rows, cols;
    getmaxyx(stdscr, rows, cols);
    baslik_ciz("HASTANIN RANDEVULARI");
    bilgi_satiri("[Herhangi bir tus] Geri");

    FILE *f = fopen(RANDEVU_DOSYA, "rb");
    if (!f) {
        attron(COLOR_PAIR(C_HATA));
        mvprintw(5, 4, "Randevu dosyasi bulunamadi.");
        attroff(COLOR_PAIR(C_HATA));
        refresh(); getch(); return;
    }

    Randevu r;
    int y = 4, bulunan = 0;
    attron(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvprintw(y, 2, "%-4s  %-9s  %-11s  %-6s  %-7s",
             "ID", "Doktor", "Tarih", "Saat", "Durum");
    attroff(A_BOLD | COLOR_PAIR(C_BASLIK));
    mvhline(y + 1, 2, ACS_HLINE, cols - 4);
    y += 2;

    while (fread(&r, sizeof(Randevu), 1, f) && y < rows - 3) {
        if (r.hasta_id == hasta_id) {
            int renk = (strcmp(r.durum, "Iptal") == 0) ? C_HATA : C_BASARI;
            attron(COLOR_PAIR(renk));
            mvprintw(y++, 2, "%-4d  %-9d  %-11s  %-6s  %-7s",
                     r.id, r.doktor_id, r.tarih, r.saat, r.durum);
            attroff(COLOR_PAIR(renk));
            bulunan++;
        }
    }
    fclose(f);

    if (bulunan) {
        attron(COLOR_PAIR(C_BILGI));
        mvprintw(rows - 3, 2, "%d randevu bulundu.", bulunan);
        attroff(COLOR_PAIR(C_BILGI));
    } else {
        attron(COLOR_PAIR(C_HATA));
        mvprintw(y, 2, "Bu hastaya ait randevu bulunamadi.");
        attroff(COLOR_PAIR(C_HATA));
    }
    refresh(); getch();
}

/* ===================== ALT MENÜLER ===================== */

void hasta_menusu() {
    const char *opts[] = {
        "Hasta Ekle",
        "Hasta Listele",
        "Hasta Ara",
        "Hasta Sil",
        "Ana Menuye Don"
    };
    while (1) {
        int s = menu_goster("HASTA ISLEMLERI", opts, 5);
        if (s < 0 || s == 4) return;
        switch (s) {
            case 0: hasta_ekle();    break;
            case 1: hasta_listele(); break;
            case 2: hasta_ara();     break;
            case 3: hasta_sil();     break;
        }
    }
}

void doktor_menusu() {
    const char *opts[] = {
        "Doktor Ekle",
        "Doktor Listele",
        "Doktor Sil",
        "Ana Menuye Don"
    };
    while (1) {
        int s = menu_goster("DOKTOR ISLEMLERI", opts, 4);
        if (s < 0 || s == 3) return;
        switch (s) {
            case 0: doktor_ekle();    break;
            case 1: doktor_listele(); break;
            case 2: doktor_sil();     break;
        }
    }
}

void randevu_menusu() {
    const char *opts[] = {
        "Randevu Al",
        "Tum Randevulari Listele",
        "Randevu Iptal Et",
        "Hastanin Randevularini Goruntule",
        "Ana Menuye Don"
    };
    while (1) {
        int s = menu_goster("RANDEVU ISLEMLERI", opts, 5);
        if (s < 0 || s == 4) return;
        switch (s) {
            case 0: randevu_al();              break;
            case 1: randevu_listele();         break;
            case 2: randevu_iptal();           break;
            case 3: randevu_hasta_goruntule(); break;
        }
    }
}

/* ===================== ANA MENU ===================== */

int main() {
    ncurses_baslat();

    const char *opts[] = {
        "Hasta Islemleri",
        "Doktor Islemleri",
        "Randevu Islemleri",
        "Cikis"
    };

    while (1) {
        int s = menu_goster("HASTANE RANDEVU SISTEMI", opts, 4);
        if (s < 0 || s == 3) break;
        switch (s) {
            case 0: hasta_menusu();   break;
            case 1: doktor_menusu();  break;
            case 2: randevu_menusu(); break;
        }
    }

    endwin();
    printf("\nGule gule!\n");
    return 0;
}
